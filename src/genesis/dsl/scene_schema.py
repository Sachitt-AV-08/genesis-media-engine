from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class SceneAsset:
    asset_id: str
    kind: str
    description: str
    source: str = "native_plan"


@dataclass
class SceneConstraints:
    duration_seconds: int = 20
    aspect_ratio: str = "9:16"
    style: str = "cinematic"
    safety_level: str = "required"


@dataclass
class Scene:
    project_id: str
    prompt: str
    title: str
    constraints: SceneConstraints
    beats: list[dict[str, Any]] = field(default_factory=list)
    assets: list[SceneAsset] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["assets"] = [asdict(asset) for asset in self.assets]
        return payload


def new_project_id(prefix: str = "genesis") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"
