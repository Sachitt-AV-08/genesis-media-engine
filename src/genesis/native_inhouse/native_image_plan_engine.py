from __future__ import annotations


class NativeImagePlanEngine:
    def plan(self, scene: dict) -> dict:
        return {
            "engine": "native_image_plan",
            "frames": [
                {"name": "opening_frame", "prompt": "Glyph on dark interface glass", "kind": "procedural"},
                {"name": "hero_frame", "prompt": f"{scene.get('title', 'Genesis')} command center reveal", "kind": "procedural"},
            ],
            "requires_model": False,
        }
