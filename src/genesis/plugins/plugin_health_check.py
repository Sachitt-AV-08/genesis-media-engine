from __future__ import annotations

import importlib.util

from .plugin_registry import default_registry


PYTHON_MODULES = {"moviepy": "moviepy", "diffusers": "diffusers"}


def plugin_health() -> dict:
    checks = []
    for plugin in default_registry.list():
        module = PYTHON_MODULES.get(plugin["name"])
        installed = importlib.util.find_spec(module) is not None if module else False
        checks.append({**plugin, "installed": installed, "usable_now": installed and plugin["enabled"]})
    return {"plugins": checks, "policy": "plugins are optional and disabled until explicitly configured"}
