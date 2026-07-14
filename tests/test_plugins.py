from genesis.plugins.plugin_health_check import plugin_health
from genesis.plugins.plugin_manifest_schema import validate_manifest
from genesis.plugins.plugin_registry import default_registry
from genesis.plugins.plugin_loader import PluginLoader


def test_plugin_registry_lists_optional_candidates():
    names = {item["name"] for item in default_registry.list()}
    assert {"moviepy", "diffusers", "comfyui"}.issubset(names)


def test_plugin_manifest_schema_requires_fields():
    assert validate_manifest({"name": "x"})["valid"] is False
    assert plugin_health()["policy"].startswith("plugins are optional")


def test_plugin_loader_discover():
    loader = PluginLoader()
    result = loader.available()
    assert isinstance(result, list)


def test_plugin_loader_load_unregistered():
    result = PluginLoader().load("nonexistent")
    assert result["loaded"] is False


def test_plugin_registry_manifest_fields():
    item = default_registry.get("moviepy")
    assert item is not None
    assert item["name"] == "moviepy"
    assert item["capability"] == "editing_render"
