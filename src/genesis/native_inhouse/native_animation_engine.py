from __future__ import annotations


class NativeAnimationEngine:
    def plan(self, scene: dict) -> dict:
        duration = scene.get("constraints", {}).get("duration_seconds", 20)
        return {
            "engine": "native_animation_plan",
            "timeline_fps": 30,
            "duration_seconds": duration,
            "tracks": [
                {"target": "glyph", "keyframes": [{"t": 0, "opacity": 0}, {"t": 2, "opacity": 1}, {"t": duration, "scale": 1.06}]},
                {"target": "panels", "keyframes": [{"t": 4, "x": -12}, {"t": 9, "x": 0}, {"t": 15, "glow": 0.42}]},
            ],
        }
