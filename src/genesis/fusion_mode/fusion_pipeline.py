from __future__ import annotations

from genesis.native_inhouse.native_animation_engine import NativeAnimationEngine
from genesis.native_inhouse.native_caption_engine import NativeCaptionEngine
from genesis.native_inhouse.native_editing_engine import NativeEditingEngine
from genesis.native_inhouse.native_image_plan_engine import NativeImagePlanEngine
from genesis.native_inhouse.native_interpolation_plan_engine import NativeInterpolationPlanEngine
from genesis.native_inhouse.native_upscale_plan_engine import NativeUpscalePlanEngine
from genesis.native_inhouse.native_video_plan_engine import NativeVideoPlanEngine
from genesis.plugins.plugin_health_check import plugin_health
from genesis.gates.final_output_gate import FinalOutputGate
from genesis.validation.render_dependency_check import render_dependencies
from genesis.validation.veda_media_validator import VedaMediaValidator

from .engine_router import EngineRouter
from .fallback_manager import FallbackManager
from .fusion_config import FusionConfig
from .fusion_events import event
from .fusion_state import FusionState
from .hybrid_render_plan import HybridRenderPlan
from .output_manifest import OutputManifestBuilder
from .provenance_tracker import ProvenanceTracker
from .quality_gate import FusionQualityGate


class FusionPipeline:
    def __init__(self, config: FusionConfig | None = None) -> None:
        self.config = config or FusionConfig()
        self.video = NativeVideoPlanEngine()

    def status(self) -> dict:
        return {
            "active": True,
            "config": self.config.to_dict(),
            "plugins": plugin_health(),
            "render_dependencies": render_dependencies(),
        }

    def plan(self, prompt: str) -> dict:
        native_plan = self.video.plan(prompt)
        scene = native_plan["scene"]
        validation = VedaMediaValidator().validate(_scene_from_dict(scene))
        image_plan = NativeImagePlanEngine().plan(scene)
        animation = NativeAnimationEngine().plan(scene)
        editing = NativeEditingEngine().plan(scene)
        captions = NativeCaptionEngine().plan(scene)
        upscale = NativeUpscalePlanEngine().plan(scene)
        interpolation = NativeInterpolationPlanEngine().plan(scene)
        hybrid = HybridRenderPlan().build(scene, animation, editing)
        package = {
            "project_id": native_plan["project_id"],
            "prompt": prompt,
            "route": EngineRouter().route(prompt),
            "scene": scene,
            "storyboard": native_plan["storyboard"],
            "image_plan": image_plan,
            "animation_plan": animation,
            "edit_plan": editing,
            "caption_plan": captions,
            "upscale_plan": upscale,
            "interpolation_plan": interpolation,
            "hybrid_render_plan": hybrid,
            "veda_validation": validation,
            "events": [event("planned", "Fusion plan created", {"project_id": native_plan["project_id"]})],
        }
        package["provenance"] = ProvenanceTracker().build(package)
        package["quality_gate"] = FusionQualityGate().review(package)
        package["manifest"] = OutputManifestBuilder().save(package)
        package["state"] = FusionState(package["project_id"], "planned", "manifest_saved", package["events"]).to_dict()
        return package

    def validate(self, prompt: str) -> dict:
        package = self.plan(prompt)
        return {"project_id": package["project_id"], "veda_validation": package["veda_validation"], "quality_gate": package["quality_gate"]}

    def render(self, prompt: str) -> dict:
        package = self.plan(prompt)
        deps = render_dependencies()
        message = FallbackManager().render_dependency_message(deps)
        approved = package["veda_validation"]["approved"] and package["quality_gate"]["approved"]
        result = {
            "ok": bool(approved and deps["can_render_video"]),
            "project_id": package["project_id"],
            "message": message,
            "approved": approved,
            "render_dependencies": deps,
            "package": package,
        }
        final_gate = FinalOutputGate().evaluate(result)
        result["final_output_gate"] = final_gate
        result["ok"] = bool(result["ok"] and final_gate["passed"])
        result["valid_final_output"] = result["ok"]
        return result

    def manifest(self, project_id: str) -> dict:
        from .output_manifest import manifest_store
        return manifest_store.get(project_id)


def _scene_from_dict(data: dict):
    from genesis.dsl.scene_schema import Scene, SceneAsset, SceneConstraints

    constraints = SceneConstraints(**data["constraints"])
    assets = [SceneAsset(**asset) for asset in data.get("assets", [])]
    return Scene(data["project_id"], data["prompt"], data["title"], constraints, data.get("beats", []), assets, data.get("metadata", {}))
