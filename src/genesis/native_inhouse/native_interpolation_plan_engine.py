from __future__ import annotations


class NativeInterpolationPlanEngine:
    def plan(self, scene: dict) -> dict:
        return {"engine": "native_interpolation_plan", "source_fps": 30, "target_fps": 30, "needs_interpolation": False}
