# Genesis Media Engine

I wanted a way to write video scripts in YAML instead of dragging things around in an editor. Genesis is what came out of that — a DSL where you describe scenes, transitions, and effects in text, then it renders them with FFmpeg.

It started as a side project for generating CODA OS promo videos, but turned into something more general. You write a scene description, it parses it, validates it through security gates, and renders output.

## How it works

You write a scene like this:

```python
from genesis.dsl.scene_parser import parse_scene_request

scene = parse_scene_request("15 second demo video, 16:9 aspect ratio")
# scene.title → "Demo Sequence"
# scene.beats → 4 timed segments with motion descriptions
# scene.assets → procedural glyphs, UI panels, motion graphics
```

The parser is deterministic — same prompt always produces the same scene structure. It extracts duration, aspect ratio, and generates beats (timed segments) with specific motion descriptions.

**Security gates** run before anything renders. The security gate checks for leaked secrets in logs (API keys, private keys, passwords), validates output paths are in safe directories, and ensures plugins are isolated. If something fails, the render doesn't happen.

```python
from genesis.gates.security_gate import SecurityGate

gate = SecurityGate()
report = gate.evaluate(render_result)
# report["passed"] → True/False
# report["issues"] → list of what failed and why
```

**Plugin system** — rendering backends are plugins. The loader discovers them, validates manifests, and runs them in sandboxed environments. Plugins can be disabled by default and only loaded when explicitly requested.

```python
from genesis.plugins.plugin_loader import PluginLoader

loader = PluginLoader()
plugins = loader.available()  # List all registered plugins
result = loader.load("ffmpeg_renderer")  # Load a specific one
```

## The parts

- **`dsl/`** — scene parser (text → structured scene), schema definitions, pre-render validation
- **`plugins/`** — plugin loader, registry, sandbox (isolated execution), manifest validation
- **`gates/`** — security gate (secret detection, path validation), benchmark gate, credibility gate, final output gate
- **`fusion_mode/`** — rendering strategies (sequential, parallel, adaptive)
- **`native_inhouse/`** — native rendering backends
- **`validation/`** — input/output validation

## Limitations

- The DSL is simple — no keyframe animation curves or complex transitions yet
- Rendering is FFmpeg-based, so no real-time GPU acceleration
- Plugin ecosystem is small — only a few built-in renderers
- No visual preview — you render the full thing to see what it looks like

## Install

```bash
pip install genesis-media-engine
# For full features:
pip install "genesis-media-engine[all]"
```

## Why "Genesis"?

Because it generates things from nothing. You start with a text prompt, and it produces a video. That felt like a genesis moment the first time it worked.
