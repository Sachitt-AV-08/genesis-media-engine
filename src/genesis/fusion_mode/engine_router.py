from __future__ import annotations

from .generation_strategy import GenerationStrategy


class EngineRouter:
    def route(self, prompt: str) -> dict:
        return GenerationStrategy().choose(prompt)
