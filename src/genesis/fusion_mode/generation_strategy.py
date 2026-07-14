from __future__ import annotations


class GenerationStrategy:
    def choose(self, prompt: str) -> dict:
        lower = prompt.lower()
        if "upscale" in lower:
            route = "native_upscale_plan"
        elif "intro" in lower or "video" in lower:
            route = "native_video_plan"
        else:
            route = "native_storyboard_plan"
        return {"route": route, "plugin_allowed": False, "reason": "native-first clean-room mode"}
