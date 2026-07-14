from __future__ import annotations

import shutil
import importlib.util


def render_dependencies() -> dict:
    ffmpeg = shutil.which("ffmpeg")
    moviepy = importlib.util.find_spec("moviepy") is not None
    return {
        "ffmpeg": {"available": bool(ffmpeg), "path": ffmpeg},
        "moviepy": {"available": moviepy},
        "can_render_video": bool(ffmpeg),
    }
