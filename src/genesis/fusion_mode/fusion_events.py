from __future__ import annotations

from datetime import datetime, timezone


def event(stage: str, message: str, payload: dict | None = None) -> dict:
    return {"stage": stage, "message": message, "payload": payload or {}, "timestamp": datetime.now(timezone.utc).isoformat()}
