from __future__ import annotations

from .scene_schema import Scene


FORBIDDEN_TERMS = ("sora", "bypass validation", "disable validation", "execute shell", "steal")


def validate_scene(scene: Scene) -> dict:
    issues: list[dict] = []
    prompt = scene.prompt.lower()
    for term in FORBIDDEN_TERMS:
        if term in prompt:
            issues.append({
                "severity": "high",
                "issue": "Unsafe or overclaiming term detected: " + term,
                "recommendation": "Rewrite the prompt and keep Genesis positioned as a validated local planning system.",
            })
    if scene.constraints.duration_seconds > 180:
        issues.append({"severity": "medium", "issue": "Duration too long for local planning demo", "recommendation": "Use a shorter proof sequence."})
    if scene.constraints.aspect_ratio not in {"9:16", "16:9", "1:1", "4:5", "21:9"}:
        issues.append({"severity": "low", "issue": "Unexpected aspect ratio", "recommendation": "Use a standard social/video aspect ratio."})
    return {
        "approved": not any(item["severity"] in {"critical", "high"} for item in issues),
        "issues": issues,
        "validator": "Genesis Scene Validator",
    }
