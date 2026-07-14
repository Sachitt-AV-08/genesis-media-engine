from __future__ import annotations

from genesis.plugins.plugin_interface import PluginManifest


class ImagePlugin:
    manifest = PluginManifest("diffusers", "image_video_generation", "Apache-2.0 code; model licenses vary", "https://github.com/huggingface/diffusers")

    def health(self) -> dict:
        return {"available": False, "reason": "wrapper only; no model downloads or pipeline auto-loads"}

    def plan(self, payload: dict) -> dict:
        return {"plugin": "diffusers", "action": "future_optional_generation", "payload_keys": sorted(payload)}
