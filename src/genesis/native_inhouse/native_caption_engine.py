from __future__ import annotations


class NativeCaptionEngine:
    def plan(self, scene: dict) -> dict:
        return {
            "engine": "native_caption_plan",
            "captions": [
                {"time": "0-4s", "text": "Genesis OS"},
                {"time": "4-12s", "text": "Building scene. Validating frames."},
                {"time": "15-20s", "text": "Launch sequence ready."},
            ],
        }
