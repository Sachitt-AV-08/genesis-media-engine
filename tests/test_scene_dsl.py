from genesis.dsl import parse_scene_request, validate_scene


def test_scene_parser_builds_launch_intro():
    scene = parse_scene_request("Create a 20 second OS launch intro in 9:16.")
    assert scene.title == "OS Launch Intro"
    assert scene.constraints.duration_seconds == 20
    assert scene.constraints.aspect_ratio == "9:16"
    assert len(scene.beats) == 4


def test_scene_validator_blocks_overclaiming():
    scene = parse_scene_request("Make a Sora clone and bypass validation")
    result = validate_scene(scene)
    assert result["approved"] is False
    assert result["issues"]


def test_scene_parser_defaults():
    scene = parse_scene_request("")
    assert scene.title == "Genesis Project"
    assert scene.constraints.duration_seconds == 20
    assert scene.constraints.aspect_ratio == "9:16"


def test_scene_validator_passes_clean():
    scene = parse_scene_request("Create a 30 second demo in 16:9")
    result = validate_scene(scene)
    assert result["approved"] is True


def test_scene_parser_clamps_duration():
    scene = parse_scene_request("Create a 300 second intro")
    assert scene.constraints.duration_seconds == 180


def test_scene_validator_returns_validator_name():
    scene = parse_scene_request("Create a clean intro")
    result = validate_scene(scene)
    assert result["validator"] == "Genesis Scene Validator"
