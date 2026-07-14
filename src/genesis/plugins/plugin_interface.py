from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class PluginManifest:
    name: str
    capability: str
    license: str
    repo_url: str
    enabled: bool = False
    notes: str = ""
    risks: list[str] = field(default_factory=list)


class GenesisPlugin(Protocol):
    manifest: PluginManifest

    def health(self) -> dict:
        ...

    def plan(self, payload: dict) -> dict:
        ...
