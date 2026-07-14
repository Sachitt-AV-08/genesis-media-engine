from __future__ import annotations

from pathlib import Path

from .reporting import now_utc, project_id_from, save_gate_report


class BenchmarkGate:
    def __init__(self, acceptable_score: int = 75) -> None:
        self.acceptable_score = acceptable_score

    def evaluate(self, render_result: dict) -> dict:
        project_id = project_id_from(render_result)
        package = render_result.get("package") or render_result.get("plan") or render_result
        scene = package.get("scene", {})
        constraints = scene.get("constraints", {})
        metadata = render_result.get("output_metadata") or package.get("output_metadata") or {}

        checks = {
            "duration_accuracy": _duration_ok(constraints, metadata),
            "aspect_ratio": _aspect_ratio_ok(constraints, metadata),
            "render_success": bool(render_result.get("ok") and render_result.get("output_path")),
            "storyboard_to_output_match": _storyboard_match(package, metadata),
            "caption_readability": _captions_readable(package),
            "output_file_validity": _output_file_valid(render_result.get("output_path")),
        }
        quality_score = round(sum(1 for value in checks.values() if value) / len(checks) * 100)
        required_checks_passed = checks["render_success"] and checks["output_file_validity"]
        issues = [
            {"severity": "medium", "issue": name.replace("_", " ") + " failed", "recommendation": _recommendation(name)}
            for name, ok in checks.items()
            if not ok
        ]
        report = {
            "project_id": project_id,
            "gate": "benchmark",
            "passed": quality_score >= self.acceptable_score and required_checks_passed,
            "acceptable_score": self.acceptable_score,
            "quality_score": quality_score,
            "required_checks_passed": required_checks_passed,
            "checks": checks,
            "issues": issues,
            "created_at": now_utc(),
        }
        report["report_path"] = save_gate_report(project_id, "benchmark_report", report)
        return report


def _duration_ok(constraints: dict, metadata: dict) -> bool:
    expected = constraints.get("duration_seconds")
    actual = metadata.get("duration_seconds")
    if expected is None or actual is None:
        return False
    return abs(float(expected) - float(actual)) <= 0.5


def _aspect_ratio_ok(constraints: dict, metadata: dict) -> bool:
    expected = constraints.get("aspect_ratio")
    actual = metadata.get("aspect_ratio")
    return bool(expected and actual and expected == actual)


def _storyboard_match(package: dict, metadata: dict) -> bool:
    storyboard = package.get("storyboard") or []
    matched = metadata.get("storyboard_beats_matched")
    if matched is None:
        return False
    return bool(storyboard) and int(matched) >= len(storyboard)


def _captions_readable(package: dict) -> bool:
    captions = package.get("caption_plan", {}).get("captions", [])
    if not captions:
        return True
    for caption in captions:
        text = str(caption.get("text", "")).strip()
        if not text or len(text) > 80:
            return False
    return True


def _output_file_valid(output_path: str | None) -> bool:
    if not output_path:
        return False
    path = Path(output_path)
    return path.exists() and path.is_file() and path.stat().st_size > 0


def _recommendation(check_name: str) -> str:
    recommendations = {
        "duration_accuracy": "Record measured output duration and keep it within 0.5s of the Scene DSL target.",
        "aspect_ratio": "Render to the Scene DSL aspect ratio.",
        "render_success": "Only mark success after the renderer creates an output file.",
        "storyboard_to_output_match": "Record how many storyboard beats are represented in the output.",
        "caption_readability": "Keep captions present, short, and readable.",
        "output_file_validity": "Verify the final output file exists and is non-empty.",
    }
    return recommendations.get(check_name, "Fix benchmark input and rerun.")
