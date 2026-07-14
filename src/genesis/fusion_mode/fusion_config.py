from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class FusionConfig:
    native_core_enabled: bool = True
    plugin_core_enabled: bool = False
    validation_required: bool = True
    executes_only_approved: bool = True
    render_mode: str = "plan_first"

    def to_dict(self) -> dict:
        return asdict(self)
