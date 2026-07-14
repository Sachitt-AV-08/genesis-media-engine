from __future__ import annotations

from genesis.native_inhouse.native_quality_engine import NativeQualityEngine


class FusionQualityGate:
    def review(self, package: dict) -> dict:
        native = NativeQualityEngine().review(package)
        plugin_risks = package.get("plugin_risks", [])
        issues = native["issues"] + [{"severity": "medium", "issue": risk, "recommendation": "Resolve plugin risk before enabling plugin."} for risk in plugin_risks]
        return {"approved": native["approved"] and not plugin_risks, "issues": issues, "gate": "fusion_quality_gate"}
