from __future__ import annotations


def native_capabilities() -> list[dict]:
    return [
        {"name": "scene_dsl", "status": "ready", "mode": "native"},
        {"name": "storyboard_planning", "status": "ready", "mode": "native"},
        {"name": "procedural_animation_plan", "status": "ready", "mode": "native"},
        {"name": "editing_plan", "status": "ready", "mode": "native"},
        {"name": "caption_plan", "status": "ready", "mode": "native"},
        {"name": "upscale_plan", "status": "ready", "mode": "native"},
        {"name": "interpolation_plan", "status": "ready", "mode": "native"},
        {"name": "quality_gate", "status": "ready", "mode": "native"},
        {"name": "pixel_video_generation", "status": "native", "mode": "ffmpeg"},
    ]
