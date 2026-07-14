from __future__ import annotations


class FallbackManager:
    def render_dependency_message(self, deps: dict) -> str:
        if deps.get("can_render_video"):
            return "Render dependencies available."
        missing = [name for name, check in deps.items() if isinstance(check, dict) and not check.get("available")]
        return f"Render plan created, but local video rendering is blocked by missing dependencies: {', '.join(missing) or 'unknown'}."
