from __future__ import annotations


class ProvenanceTracker:
    def build(self, package: dict) -> dict:
        return {
            "native_components": [
                "Scene DSL",
                "Native storyboard planner",
                "Native animation planner",
                "Native editing planner",
                "Media validator",
            ],
            "plugin_components": package.get("plugins_used", []),
            "unknown_assets": [],
            "disclosures": [
                "No Sora-level model is claimed.",
                "Optional plugins remain disabled unless explicitly configured.",
                "Render execution requires validation approval.",
            ],
        }
