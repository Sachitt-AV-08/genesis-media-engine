from __future__ import annotations


class NativeEditingEngine:
    def plan(self, scene: dict) -> dict:
        return {
            "engine": "native_editing_plan",
            "cuts": [{"after_beat": beat.get("index"), "transition": "match_glow"} for beat in scene.get("beats", [])[:-1]],
            "audio": {"bed": "low_pulse", "hit_points": ["4s", "9s", "15s"], "requires_external_asset": False},
            "requires_ffmpeg": True,
        }
