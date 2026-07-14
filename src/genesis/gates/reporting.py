from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


REPORT_ROOT = Path("reports/genesis")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_gate_report(project_id: str, report_name: str, payload: dict) -> str:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORT_ROOT / f"{project_id}_{report_name}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    latest_path = REPORT_ROOT / f"{report_name}.json"
    latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)


def project_id_from(payload: dict) -> str:
    return payload.get("project_id") or payload.get("package", {}).get("project_id") or payload.get("plan", {}).get("project_id") or "genesis_unknown"
