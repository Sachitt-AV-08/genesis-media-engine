from __future__ import annotations


REQUIRED_MANIFEST_FIELDS = {"name", "capability", "license", "repo_url", "enabled"}


def validate_manifest(manifest: dict) -> dict:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    return {"valid": not missing, "missing": missing}
