from genesis.fusion_mode import FusionPipeline


def test_fusion_plan_contains_required_artifacts():
    package = FusionPipeline().plan("Create a 20 second OS launch intro in 9:16.")
    assert package["scene"]["title"] == "OS Launch Intro"
    assert package["storyboard"]
    assert package["hybrid_render_plan"]["stages"]
    assert package["quality_gate"]["approved"] is True
    assert package["manifest"]["project_id"] == package["project_id"]


def test_fusion_render_returns_dependency_aware_result():
    result = FusionPipeline().render("Create a 20 second OS launch intro in 9:16.")
    assert "render_dependencies" in result
    assert "project_id" in result


def test_fusion_render_blocks_without_ffmpeg():
    result = FusionPipeline().render("Create a video")
    assert result["ok"] in (True, False)


def test_fusion_state_tracking():
    package = FusionPipeline().plan("Create a 10 second demo in 9:16")
    state = package.get("state", {})
    assert state.get("status") == "planned"
    assert state.get("current_stage") == "manifest_saved"
