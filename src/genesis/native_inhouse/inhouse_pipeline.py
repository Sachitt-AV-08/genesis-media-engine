from __future__ import annotations

from genesis.native_inhouse.native_animation_engine import NativeAnimationEngine
from genesis.native_inhouse.native_caption_engine import NativeCaptionEngine
from genesis.native_inhouse.native_editing_engine import NativeEditingEngine
from genesis.native_inhouse.native_image_plan_engine import NativeImagePlanEngine
from genesis.native_inhouse.native_interpolation_plan_engine import NativeInterpolationPlanEngine
from genesis.native_inhouse.native_quality_engine import NativeQualityEngine
from genesis.native_inhouse.native_upscale_plan_engine import NativeUpscalePlanEngine
from genesis.native_inhouse.native_renderer import NativeRenderer
from genesis.native_inhouse.native_video_plan_engine import NativeVideoPlanEngine
from genesis.gates.final_output_gate import FinalOutputGate
from genesis.validation.render_dependency_check import render_dependencies
from genesis.validation.veda_media_validator import VedaMediaValidator
from genesis.fusion_mode.provenance_tracker import ProvenanceTracker
from genesis.fusion_mode.output_manifest import ProvenanceManifest, manifest_store


class InHousePipeline:
    def __init__(self) -> None:
        self.video = NativeVideoPlanEngine()

    def status(self) -> dict:
        return {"active": True, "mode": "native_inhouse", "render_dependencies": render_dependencies()}

    def plan(self, prompt: str) -> dict:
        base = self.video.plan(prompt)
        scene = base["scene"]
        package = {
            **base,
            "image_plan": NativeImagePlanEngine().plan(scene),
            "animation_plan": NativeAnimationEngine().plan(scene),
            "edit_plan": NativeEditingEngine().plan(scene),
            "caption_plan": NativeCaptionEngine().plan(scene),
            "upscale_plan": NativeUpscalePlanEngine().plan(scene),
            "interpolation_plan": NativeInterpolationPlanEngine().plan(scene),
        }
        package["veda_validation"] = VedaMediaValidator().validate(_scene_from_dict(scene))
        package["quality_gate"] = NativeQualityEngine().review(package)
        package["provenance"] = ProvenanceTracker().build(package)
        manifest = ProvenanceManifest(
            project_id=package["project_id"],
            mode="native_inhouse",
            native_components=["Scene DSL", "storyboard", "animation", "editing", "captions", "quality", "validator"],
            plugin_components=[],
            disclosures=["Clean-room native plan; no third-party model output claimed."],
            outputs={"scene": scene, "storyboard": package["storyboard"], "quality_gate": package["quality_gate"]},
        )
        package["manifest"] = manifest_store.save(manifest)
        return package

    def storyboard(self, prompt: str) -> dict:
        plan = self.plan(prompt)
        return {"project_id": plan["project_id"], "storyboard": plan["storyboard"]}

    def render_plan(self, prompt: str) -> dict:
        plan = self.plan(prompt)
        return {
            "project_id": plan["project_id"],
            "scene": plan["scene"],
            "animation_plan": plan["animation_plan"],
            "edit_plan": plan["edit_plan"],
            "caption_plan": plan["caption_plan"],
            "dependencies": render_dependencies(),
        }

    def render(self, prompt: str, output_path: str | Path = "output/genesis_render.mp4") -> dict:
        plan = self.plan(prompt)
        renderer = NativeRenderer()
        if not renderer.available:
            result = {
                "ok": False,
                "project_id": plan["project_id"],
                "message": "Render plan created, but FFmpeg is not available for local video output. Install FFmpeg and ensure it is on PATH.",
                "approved": plan["veda_validation"]["approved"] and plan["quality_gate"]["approved"],
                "dependencies": render_dependencies(),
                "plan": plan,
                "render_available": False,
            }
            result["final_output_gate"] = FinalOutputGate().evaluate(result)
            result["valid_final_output"] = False
            return result
        render_result = renderer.render(plan, output_path)
        final_gate = FinalOutputGate().evaluate(render_result)
        render_result["final_output_gate"] = final_gate
        render_result["project_id"] = plan["project_id"]
        render_result["valid_final_output"] = bool(render_result.get("ok") and final_gate["passed"])
        return render_result

    def manifest(self, project_id: str) -> dict:
        return manifest_store.get(project_id)


def _scene_from_dict(data: dict):
    from genesis.dsl.scene_schema import Scene, SceneAsset, SceneConstraints

    constraints = SceneConstraints(**data["constraints"])
    assets = [SceneAsset(**asset) for asset in data.get("assets", [])]
    return Scene(data["project_id"], data["prompt"], data["title"], constraints, data.get("beats", []), assets, data.get("metadata", {}))
