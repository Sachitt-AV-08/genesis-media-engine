from __future__ import annotations

from dataclasses import asdict

from .plugin_interface import PluginManifest


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginManifest] = {}

    def register(self, manifest: PluginManifest) -> None:
        self._plugins[manifest.name] = manifest

    def list(self) -> list[dict]:
        return [asdict(item) for item in self._plugins.values()]

    def get(self, name: str) -> dict | None:
        item = self._plugins.get(name)
        return asdict(item) if item else None


default_registry = PluginRegistry()
for item in [
    PluginManifest("moviepy", "editing_render", "MIT", "https://github.com/Zulko/moviepy", notes="Optional local editing/render plugin."),
    PluginManifest("diffusers", "image_video_generation", "Apache-2.0 code; model licenses vary", "https://github.com/huggingface/diffusers", risks=["model license check required"]),
    PluginManifest("comfyui", "workflow_engine", "GPL-3.0", "https://github.com/comfy-org/ComfyUI", risks=["keep isolated from core"]),
    PluginManifest("wan2_1", "text_image_to_video", "Apache-2.0 family", "https://github.com/Wan-Video/Wan2.1", risks=["large weights and GPU required"]),
    PluginManifest("realesrgan_ncnn", "upscaling", "MIT", "https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan"),
]:
    default_registry.register(item)
