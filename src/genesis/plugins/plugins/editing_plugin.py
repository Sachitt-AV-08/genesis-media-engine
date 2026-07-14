from __future__ import annotations

import importlib.util

from genesis.plugins.plugin_interface import PluginManifest


class EditingPlugin:
    manifest = PluginManifest("moviepy", "editing_render", "MIT", "https://github.com/Zulko/moviepy")

    def health(self) -> dict:
        return {"available": importlib.util.find_spec("moviepy") is not None, "auto_execute": False}

    def plan(self, payload: dict) -> dict:
        return {"plugin": "moviepy", "action": "future_optional_render", "requires_validation_approval": True}
