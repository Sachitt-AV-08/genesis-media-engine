from genesis.native_inhouse.inhouse_pipeline import InHousePipeline


def test_inhouse_pipeline_plan_is_native_only():
    package = InHousePipeline().plan("Create a 20 second OS launch intro in 9:16.")
    assert package["scene"]["metadata"]["neural_generation"] is False
    assert package["veda_validation"]["approved"] is True
    assert package["manifest"]["plugin_components"] == []


def test_inhouse_render_plan_has_dependencies():
    payload = InHousePipeline().render_plan("Create a 20 second OS launch intro in 9:16.")
    assert payload["dependencies"]
    assert payload["animation_plan"]["timeline_fps"] == 30


def test_inhouse_pipeline_status():
    status = InHousePipeline().status()
    assert status["active"] is True
    assert status["mode"] == "native_inhouse"
