from __future__ import annotations

from genesis.plugins.plugin_interface import PluginManifest


class VideoPlugin:
    manifest = PluginManifest("wan2_1", "text_image_to_video", "Apache-2.0 family", "https://github.com/Wan-Video/Wan2.1")

    def health(self) -> dict:
        return {"available": False, "reason": "large video model not downloaded; plugin disabled by default"}

    def plan(self, payload: dict) -> dict:
        return {"plugin": "wan2_1", "action": "future_optional_video_generation", "requires_gpu": True}
