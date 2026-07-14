from __future__ import annotations


class HybridRenderPlan:
    def build(self, scene: dict, animation: dict, editing: dict) -> dict:
        return {
            "mode": "native_first_optional_plugin",
            "scene_id": scene.get("project_id"),
            "stages": [
                {"stage": "procedural_background", "engine": "native", "status": "planned"},
                {"stage": "ui_motion_graphics", "engine": "native", "status": "planned"},
                {"stage": "timeline_edit", "engine": "moviepy_or_ffmpeg_optional", "status": "dependency_checked"},
                {"stage": "upscale", "engine": "native_plan_or_optional_plugin", "status": "planned"},
            ],
            "animation": animation,
            "editing": editing,
        }
