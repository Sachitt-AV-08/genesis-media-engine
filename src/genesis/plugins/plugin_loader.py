from __future__ import annotations

from pathlib import Path
from .plugin_registry import default_registry


class PluginLoader:
    def available(self) -> list[dict]:
        return default_registry.list()

    def load(self, name: str) -> dict:
        plugin = default_registry.get(name)
        if not plugin:
            return {"loaded": False, "reason": "plugin not registered"}
        if not plugin.get("enabled"):
            return {"loaded": False, "plugin": plugin, "reason": "plugin is optional and disabled by default"}
        return {"loaded": True, "plugin": plugin}

    def discover(self, directory: str | Path) -> list[str]:
        dirpath = Path(directory)
        if not dirpath.is_dir():
            return []
        discovered = []
        for p in dirpath.glob("*.py"):
            if p.name.startswith("_"):
                continue
            discovered.append(p.stem)
        return discovered
