[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

# Genesis Media Engine

**DSL-driven media generation engine** with FFmpeg rendering, plugin system, and provenance tracking. Write scene scripts in a declarative DSL, render with native or GPU-accelerated pipelines, and verify output with security gates.

## Features

- **Declarative DSL** — describe scenes, transitions, and effects in YAML/JSON scripts
- **Plugin System** — load, sandbox, and manage rendering plugins with manifest validation
- **Security Gates** — benchmark, credibility, and final output validation before delivery
- **FFmpeg Rendering** — native FFmpeg integration for video/audio/image output
- **Provenance Tracking** — full audit trail from scene script to final output
- **Scene Validation** — schema-based validation of scene descriptions before rendering
- **Fusion Modes** — multiple rendering strategies (sequential, parallel, adaptive)

## Install

```bash
pip install genesis-media-engine
```

### Optional extras

```bash
pip install "genesis-media-engine[all]"    # moviepy + diffusers + torch
```

## Quickstart

```python
from genesis.dsl.scene_parser import SceneParser
from genesis.plugins.plugin_loader import PluginLoader

# Define a scene
scene = """
scene:
  name: "intro"
  duration: 10
  layers:
    - type: image
      source: "background.png"
      opacity: 1.0
    - type: text
      content: "Hello World"
      position: center
      animation: fade_in
"""

# Parse and render
parser = SceneParser()
parsed = parser.parse(scene)
# Render with FFmpeg or plugin pipeline
```

## Architecture

```
genesis/
├── dsl/
│   ├── scene_parser.py        # DSL → scene graph
│   ├── scene_schema.py        # Schema definitions
│   └── scene_validator.py     # Pre-render validation
├── plugins/
│   ├── plugin_interface.py    # Plugin base class
│   ├── plugin_loader.py       # Dynamic plugin loading
│   ├── plugin_registry.py     # Plugin discovery
│   ├── plugin_sandbox.py      # Isolated execution
│   └── plugin_manifest_schema.py  # Manifest validation
├── gates/
│   ├── benchmark_gate.py      # Performance validation
│   ├── credibility_gate.py    # Output quality checks
│   ├── final_output_gate.py   # Pre-delivery verification
│   ├── security_gate.py       # Safety validation
│   └── reporting.py           # Gate result reporting
├── fusion_mode/               # Rendering strategies
├── native_inhouse/            # Native rendering backends
└── validation/                # Input/output validation
```

## DSL Example

```yaml
scene:
  name: "product_reveal"
  duration: 15
  fps: 30
  layers:
    - type: video
      source: "background.mp4"
      trim: [0, 15]
    - type: image
      source: "product.png"
      position: [0.5, 0.5]
      animation:
        type: scale
        from: 0.0
        to: 1.0
        duration: 2.0
    - type: text
      content: "Introducing Product X"
      font: "Arial Bold"
      size: 48
      animation:
        type: fade_in
        delay: 3.0
  transitions:
    - type: crossfade
      duration: 1.0
```

## Plugin Development

```python
from genesis.plugins.plugin_interface import PluginInterface

class MyRenderer(PluginInterface):
    name = "custom_renderer"
    version = "1.0.0"

    def render(self, scene, output_path):
        # Custom rendering logic
        pass

    def validate(self, scene):
        # Pre-render validation
        return True
```

## Development

```bash
git clone https://github.com/Sachitt-AV-08/genesis-media-engine.git
cd genesis-media-engine
pip install -e ".[dev]"
python -m pytest tests/
```

## License

MIT
