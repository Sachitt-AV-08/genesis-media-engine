from __future__ import annotations

from genesis.dsl.scene_validator import validate_scene


class VedaMediaValidator:
    def validate(self, scene_obj) -> dict:
        result = validate_scene(scene_obj)
        result["validation_status"] = "approved" if result["approved"] else "blocked"
        result["rule"] = "Validation approval required before render execution."
        return result
