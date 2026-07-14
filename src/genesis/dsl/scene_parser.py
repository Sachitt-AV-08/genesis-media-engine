from __future__ import annotations

import re

from .scene_schema import Scene, SceneAsset, SceneConstraints, new_project_id


def _duration_seconds(text: str) -> int:
    match = re.search(r"(\d+)\s*(second|sec|s)\b", text, re.IGNORECASE)
    if match:
        return max(3, min(180, int(match.group(1))))
    return 20


def _aspect_ratio(text: str) -> str:
    match = re.search(r"\b(9:16|16:9|1:1|4:5|21:9)\b", text)
    return match.group(1) if match else "9:16"


def parse_scene_request(prompt: str) -> Scene:
    clean_prompt = (prompt or "").strip()
    lower = clean_prompt.lower()
    title = "Genesis Project"
    if "launch" in lower and ("intro" in lower or "os" in lower):
        title = "OS Launch Intro"
    elif "demo" in lower:
        title = "Demo Sequence"

    duration = _duration_seconds(clean_prompt)
    aspect = _aspect_ratio(clean_prompt)
    beats = [
        {"index": 1, "time": "0-4s", "description": "Dark interface wake-up with glyph pulse", "motion": "slow push-in"},
        {"index": 2, "time": "4-9s", "description": "Build lines and validation marks cross-check the scene", "motion": "layered parallax"},
        {"index": 3, "time": "9-15s", "description": "Shell assembles into a focused command center", "motion": "snap-grid reveal"},
        {"index": 4, "time": f"15-{duration}s", "description": "Final mark, launch title, and clean exit frame", "motion": "hold with subtle shimmer"},
    ]
    assets = [
        SceneAsset("glyph", "procedural_shape", "Brand mark built from simple lines and glow masks"),
        SceneAsset("panels", "procedural_ui", "Layered panel and status rails"),
        SceneAsset("signals", "motion_graphics", "Contrasting validation signal paths"),
    ]
    return Scene(
        project_id=new_project_id(),
        prompt=clean_prompt,
        title=title,
        constraints=SceneConstraints(duration_seconds=duration, aspect_ratio=aspect),
        beats=beats,
        assets=assets,
        metadata={"parser": "deterministic_v1", "neural_generation": False},
    )
