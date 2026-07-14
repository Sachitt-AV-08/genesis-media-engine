from __future__ import annotations


class NativeQualityEngine:
    def review(self, package: dict) -> dict:
        issues: list[dict] = []
        scene = package.get("scene", {})
        if not scene.get("beats"):
            issues.append({"severity": "high", "issue": "No storyboard beats generated", "recommendation": "Regenerate the scene plan."})
        if package.get("provenance", {}).get("unknown_assets"):
            issues.append({"severity": "medium", "issue": "Unknown asset source", "recommendation": "Attach provenance before render."})
        return {"approved": not any(i["severity"] == "high" for i in issues), "issues": issues, "gate": "native_quality_engine"}
