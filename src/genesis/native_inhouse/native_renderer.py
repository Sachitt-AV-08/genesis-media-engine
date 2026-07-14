from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from genesis.validation.render_dependency_check import render_dependencies


class NativeRenderer:
    def __init__(self) -> None:
        deps = render_dependencies()
        self.ffmpeg = deps.get("ffmpeg", {}).get("path") or shutil.which("ffmpeg")
        self.available = bool(self.ffmpeg)

    def status(self) -> dict:
        return {"available": self.available, "ffmpeg_path": self.ffmpeg}

    def render(self, plan: dict, output_path: str | Path = "output/genesis_render.mp4") -> dict:
        if not self.available:
            return {
                "ok": False,
                "error": "FFmpeg not available",
                "plan_only": True,
            }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        scene = plan.get("scene", {})
        beats = scene.get("beats", [])
        edit_plan = plan.get("edit_plan", {})
        quality_gate = plan.get("quality_gate", {})
        validation = plan.get("veda_validation", {})
        approved = validation.get("approved", False) and quality_gate.get("approved", False)

        if not approved:
            return {
                "ok": False,
                "error": "Plan not approved by validation/quality gate",
                "approved": approved,
            }

        if not beats:
            return {"ok": False, "error": "No scene beats to render."}

        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as _tmpdir:
            inputs, filters, labels, segments = self._build_filter_graph(beats, edit_plan, _tmpdir)

            if not inputs:
                return {"ok": False, "error": "No video input from scene beats."}

            cmd = [self.ffmpeg, "-y"]
            for inp in inputs:
                if isinstance(inp, dict):
                    cmd.extend(["-i", inp["path"]])
                else:
                    cmd.extend(["-f", "lavfi", "-i", inp])

            filter_str = ";".join(filters) if filters else ""
            if filter_str:
                last_label = labels[-1] if labels else "v"
                cmd.extend(["-filter_complex", filter_str, "-map", f"[{last_label}]"])

            encoder, enc_args = self._detect_encoder()
            cmd.extend(["-c:v", encoder] + enc_args)

            duration = max((b.get("duration", 3) for b in beats), default=5)
            cmd.extend(["-t", str(duration)])
            cmd.extend(["-movflags", "+faststart", str(output_path)])

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                if result.returncode != 0:
                    return {
                        "ok": False,
                        "error": result.stderr[-500:] if result.stderr else "FFmpeg error",
                        "cmd_summary": " ".join(str(c) for c in cmd[:8]) + "...",
                    }
                return {
                    "ok": True,
                    "output_path": str(output_path),
                    "size_bytes": output_path.stat().st_size,
                    "duration": duration,
                    "beats_rendered": len(beats),
                    "encoder": encoder,
                }
            except subprocess.TimeoutExpired:
                return {"ok": False, "error": "FFmpeg timed out (180s)"}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

    def _detect_encoder(self) -> tuple[str, list[str]]:
        try:
            probe = subprocess.run(
                [self.ffmpeg, "-encoders"], capture_output=True, text=True, timeout=10
            )
            encoders = probe.stdout
            if "h264_nvenc" in encoders:
                return ("h264_nvenc", ["-preset", "p7", "-cq", "23", "-pix_fmt", "yuv420p"])
            if "h264_qsv" in encoders:
                return ("h264_qsv", ["-preset", "medium", "-global_quality", "23", "-pix_fmt", "yuv420p"])
            if "h264_amf" in encoders:
                return ("h264_amf", ["-quality", "quality", "-rc", "cqp", "-qp_i", "23", "-qp_p", "23"])
        except Exception:
            pass
        return ("libx264", ["-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p"])

    def _build_filter_graph(
        self, beats: list[dict], edit_plan: dict, tmpdir: str
    ) -> tuple[list, list[str], list[str], list[dict]]:
        inputs: list = []
        filters: list[str] = []
        labels: list[str] = []
        segments: list[dict] = []

        transition = edit_plan.get("transition", "fade")
        prev_label = None

        for i, beat in enumerate(beats):
            dur = beat.get("duration", 3)
            source = beat.get("source") or beat.get("video_path")
            seg_label = f"s{i}"

            if source and Path(source).exists():
                inputs.append({"path": source, "stream": "v"})
                dur = beat.get("duration", 0)
                actual_dur = self._get_video_duration(source)
                if dur <= 0:
                    dur = actual_dur
                filters.append(
                    f"[{i}:v]trim=duration={dur},setpts=PTS-STARTPTS[{seg_label}_trim]"
                )
                labels.append(f"{seg_label}_trim")
            else:
                color = beat.get("bg_color", "0x222222")
                size = beat.get("resolution", "1920x1080")
                inputs.append(f"color=c={color}:s={size}:d={dur},format=yuv420p")
                labels.append(f"{i}:v")
                segments.append({"type": "color", "duration": dur})

            if prev_label is not None and i > 0:
                trans = self._build_transition(prev_label, labels[-1], transition, dur)
                if trans:
                    filters.append(trans["filter"])
                    prev_label = trans["label"]
            else:
                prev_label = labels[-1]

            text_content = beat.get("text") or beat.get("title") or edit_plan.get("text")
            if text_content:
                text_filter, text_label = self._build_text_overlay(prev_label, text_content)
                filters.append(text_filter)
                prev_label = text_label

            captions = edit_plan.get("captions", [])
            for cap_idx, cap in enumerate(captions):
                cap_text = cap.get("text", "")
                cap_start = cap.get("start", 0)
                cap_dur = cap.get("duration", 3)
                if cap_text:
                    cf, cl = self._build_caption_overlay(prev_label, cap_text, cap_start, cap_dur)
                    filters.append(cf)
                    prev_label = cl

            color_grade = edit_plan.get("color_grade", {})
            if color_grade:
                cgf, cgl = self._build_color_grade(prev_label, color_grade)
                filters.append(cgf)
                prev_label = cgl

        if len(labels) > 1:
            concat_parts = "".join(f"[{lbl}]" for lbl in labels)
            filters.append(f"{concat_parts}concat=n={len(labels)}:v=1:a=0[{prev_label}_out]")
            prev_label = f"{prev_label}_out"

        return inputs, filters, [prev_label], segments

    def _build_transition(self, from_label: str, to_label: str, trans_type: str, duration: float) -> dict | None:
        xfade_map = {
            "fade": "fade",
            "dissolve": "dissolve",
            "wipeleft": "wipeleft",
            "wiperight": "wiperight",
            "slideleft": "slideleft",
            "slideright": "slideright",
            "fadeblack": "fadeblack",
            "fadewhite": "fadewhite",
            "radial": "radial",
            "circleclose": "circleclose",
            "circleopen": "circleopen",
        }
        xfade_type = xfade_map.get(trans_type, "fade")
        trans_dur = min(0.5, duration * 0.3)
        label = f"t_{from_label}_{to_label}"
        return {
            "filter": f"[{from_label}][{to_label}]xfade=transition={xfade_type}:duration={trans_dur}:offset={max(0, duration - trans_dur)}[{label}]",
            "label": label,
        }

    def _build_text_overlay(self, in_label: str, text: str) -> tuple[str, str]:
        label = f"txt_{in_label}"
        safe_text = text.replace("'", "\\'").replace(":", "\\:")
        return (
            f"[{in_label}]drawtext=text='{safe_text}':"
            f"fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-th-100:"
            f"shadowy=2:shadowcolor=black@0.5[{label}]",
            label,
        )

    def _build_caption_overlay(self, in_label: str, text: str, start: float, duration: float) -> tuple[str, str]:
        label = f"cap_{in_label}"
        safe_text = text.replace("'", "\\'").replace(":", "\\:")
        return (
            f"[{in_label}]drawtext=text='{safe_text}':"
            f"fontsize=36:fontcolor=white:x=(w-text_w)/2:y=h-th-50:"
            f"enable='between(t,{start},{start + duration})':shadowy=2:shadowcolor=black@0.5[{label}]",
            label,
        )

    def _build_color_grade(self, in_label: str, grade: dict) -> tuple[str, str]:
        label = f"cg_{in_label}"
        brightness = grade.get("brightness", 0.0)
        contrast = grade.get("contrast", 1.0)
        saturation = grade.get("saturation", 1.0)
        gamma = grade.get("gamma", 1.0)
        eq_str = f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}:gamma={gamma}"
        return (f"[{in_label}]{eq_str}[{label}]", label)

    def _get_video_duration(self, path: str | Path) -> float:
        try:
            result = subprocess.run(
                [self.ffmpeg, "-i", str(path)],
                capture_output=True, text=True, timeout=10,
            )
            import re
            match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", result.stderr)
            if match:
                h, m, s = match.groups()
                return int(h) * 3600 + int(m) * 60 + float(s)
        except Exception:
            pass
        return 5.0
