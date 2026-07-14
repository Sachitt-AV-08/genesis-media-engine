# Genesis Media Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/genesis-media-engine/genesis/actions/workflows/test.yml/badge.svg)](https://github.com/genesis-media-engine/genesis/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

DSL-driven media generation engine with FFmpeg rendering, plugin system, and provenance tracking.

## What is Genesis?

Genesis is a standalone engine that converts structured scene descriptions (DSL) into rendered video output. It was extracted from a larger experimental system — all CODA-specific cognitive pipelines, agent references, and internal coupling have been removed.

The core insight: describe your scene in a simple JSON-like DSL, validate it, plan it, and render it — all with traceable provenance from scene to pixel.

## Scene DSL Example

```python
from genesis.dsl import parse_scene_request, validate_scene

scene = parse_scene_request("Create a 30 second product showcase in 16:9")
result = validate_scene(scene)
if result["approved"]:
    print(f"Ready: {scene.title} ({scene.constraints.duration_seconds}s)")
```

A scene has beats (timeline segments), assets (media elements), and constraints (duration, aspect ratio, style).

## Architecture

```
┌──────────┐    ┌─────────────┐    ┌──────────────────────────┐
│  Scene   │ →  │   Validate  │ →  │  Render Plan (Native /   │
│  DSL     │    │  + Plan     │    │  Fusion / Plugin)        │
└──────────┘    └─────────────┘    └───────────┬──────────────┘
                                               ↓
┌──────────┐    ┌─────────────┐    ┌──────────────────────────┐
│  Output  │ ←  │  Gates      │ ←  │  FFmpeg / MoviePy /      │
│  File    │    │  (Qual/Sec) │    │  Plugin Renderer         │
└──────────┘    └─────────────┘    └──────────────────────────┘
```

### DSL Module
Scene schema, parser, and validator — turns text prompts into structured `Scene` objects.

### Native Inhouse Pipeline
Built-in planning engines for video, image, animation, editing, captions, upscaling, and interpolation. The `NativeRenderer` uses FFmpeg for actual video output.

### Fusion Mode
Combined pipeline that routes through native + optional plugin engines, tracks provenance, builds manifests, and passes through quality/security gates.

### Plugins
Plugin system with sandboxed execution, manifest validation, and directory-based discovery. Bundled plugins for editing (MoviePy), image generation (Diffusers), and video generation (Wan2.1).

### Gates
Four gates run before final output: Security (secrets scan, path safety, plugin isolation), Credibility (disclosure verification, output mode classification), Benchmark (duration, aspect ratio, caption readability), and Final Output Gate (aggregates all gates).

## Quickstart

```bash
pip install genesis-media-engine

# Ensure FFmpeg is on PATH (optional — plan-only mode works without it)
# Render a scene
python -m genesis plan "Create a 20 second intro in 9:16" --render output.mp4

# Use the pipeline programmatically
python
>>> from genesis.native_inhouse import InHousePipeline
>>> result = InHousePipeline().plan("Create a 10 second demo")
>>> result["scene"]["title"]
'CODA OS Launch Intro'
```

## Plugin Development

Plugins implement the `GenesisPlugin` protocol:

```python
from genesis.plugins.plugin_interface import PluginManifest, GenesisPlugin

class MyPlugin:
    manifest = PluginManifest(
        name="my_plugin",
        capability="custom_effect",
        license="MIT",
        repo_url="https://github.com/me/my-plugin",
    )

    def health(self) -> dict:
        return {"available": True}

    def plan(self, payload: dict) -> dict:
        return {"plugin": "my_plugin", "action": "custom_effect"}
```

Place plugins in a directory and point `GENESIS_PLUGIN_DIR` at it — the loader discovers them automatically.

## Render Dependencies

- **FFmpeg** (optional): required only for video rendering. Install via `choco install ffmpeg` (Windows), `brew install ffmpeg` (macOS), or `apt install ffmpeg` (Linux).
- **MoviePy** (optional): bundled plugin for Python-native rendering.

Without FFmpeg, all planning and validation work. Rendering returns a useful error pointing to the missing dependency.

## Testing

```bash
pip install -e ".[dev]"
pytest
```
