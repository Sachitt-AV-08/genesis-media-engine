from __future__ import annotations


class NativeUpscalePlanEngine:
    def plan(self, scene: dict) -> dict:
        return {"engine": "native_upscale_plan", "target": "1080x1920", "method": "plugin_optional", "native_now": "bicubic_placeholder_plan"}
