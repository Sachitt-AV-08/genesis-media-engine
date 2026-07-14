from __future__ import annotations

from genesis.dsl.scene_parser import parse_scene_request


class NativeVideoPlanEngine:
    def plan(self, prompt: str) -> dict:
        scene = parse_scene_request(prompt)
        storyboard = [
            {"shot": beat["index"], "duration": beat["time"], "visual": beat["description"], "camera": beat.get("motion", "locked")}
            for beat in scene.beats
        ]
        return {
            "project_id": scene.project_id,
            "scene": scene.to_dict(),
            "storyboard": storyboard,
            "engine": "native_video_plan",
            "renderable_now": False,
            "message": "Render plan created. Pixel rendering requires FFmpeg.",
        }
