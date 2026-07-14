from __future__ import annotations

from pathlib import Path
import re

from genesis.validation.render_dependency_check import render_dependencies

from .reporting import now_utc, project_id_from, save_gate_report


SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*[A-Za-z0-9_./+=-]{8,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


class SecurityGate:
    def __init__(self, safe_output_root: str | Path = "output/genesis") -> None:
        self.safe_output_root = Path(safe_output_root).resolve()

    def evaluate(self, render_result: dict) -> dict:
        project_id = project_id_from(render_result)
        package = render_result.get("package") or render_result.get("plan") or render_result
        deps = render_result.get("render_dependencies") or render_result.get("dependencies") or render_dependencies()
        output_path = render_result.get("output_path")
        checks = {
            "validation_approval": bool(package.get("veda_validation", {}).get("approved")),
            "execution_after_approval": bool(render_result.get("approved") and package.get("veda_validation", {}).get("approved")),
            "prevent_destructive_overwrite": _overwrite_safe(render_result),
            "safe_output_folder": _safe_output_path(output_path, self.safe_output_root),
            "plugin_isolation": _plugin_isolation_ok(package),
            "dependency_availability": bool(deps.get("can_render_video")),
            "no_secrets_in_logs": not _contains_secret(render_result),
        }
        issues = [
            {"severity": "high", "issue": name.replace("_", " ") + " failed", "recommendation": _recommendation(name)}
            for name, ok in checks.items()
            if not ok
        ]
        passed = not issues
        report = {
            "project_id": project_id,
            "gate": "security",
            "passed": passed,
            "checks": checks,
            "safe_output_root": str(self.safe_output_root),
            "issues": issues,
            "created_at": now_utc(),
        }
        report["report_path"] = save_gate_report(project_id, "security_report", report)
        return report


def _overwrite_safe(render_result: dict) -> bool:
    if not render_result.get("would_overwrite"):
        return True
    return bool(render_result.get("overwrite_allowed") or render_result.get("backup_created"))


def _safe_output_path(output_path: str | None, safe_root: Path) -> bool:
    if not output_path:
        return True
    try:
        return Path(output_path).resolve().is_relative_to(safe_root)
    except ValueError:
        return False


def _plugin_isolation_ok(package: dict) -> bool:
    plugin_components = package.get("manifest", {}).get("plugin_components") or package.get("provenance", {}).get("plugin_components") or []
    if not plugin_components:
        return True
    plugin_status = package.get("plugins", {}) or package.get("plugin_status", {})
    return bool(plugin_status.get("isolated") or package.get("plugin_isolation") == "process_boundary")


def _contains_secret(payload) -> bool:
    text = _flatten_text(payload)
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def _flatten_text(value) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten_text(item) for item in value.values())
    if isinstance(value, list | tuple | set):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)


def _recommendation(check_name: str) -> str:
    recommendations = {
        "validation_approval": "Require validation approval before final render success.",
        "execution_after_approval": "Execution must be recorded only after validation approval.",
        "prevent_destructive_overwrite": "Write to a new output path or explicitly enable controlled overwrite with backup.",
        "safe_output_folder": "Write final media only under output/genesis.",
        "plugin_isolation": "Run plugins in a declared process boundary or keep them disabled.",
        "dependency_availability": "Install and verify FFmpeg/MoviePy before final video output.",
        "no_secrets_in_logs": "Remove raw credentials from logs and reports.",
    }
    return recommendations.get(check_name, "Fix security check and rerun.")
