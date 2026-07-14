from __future__ import annotations

from .reporting import now_utc, project_id_from, save_gate_report


class CredibilityGate:
    def evaluate(self, render_result: dict) -> dict:
        project_id = project_id_from(render_result)
        package = render_result.get("package") or render_result.get("plan") or render_result
        manifest = package.get("manifest", {})
        provenance = package.get("provenance", {})
        native_components = manifest.get("native_components") or provenance.get("native_components") or []
        plugin_components = manifest.get("plugin_components") or provenance.get("plugin_components") or package.get("plugins_used", [])
        disclosures = manifest.get("disclosures") or provenance.get("disclosures") or []
        output_mode = self.classify_output_mode(native_components, plugin_components)

        issues: list[dict] = []
        if not native_components and not plugin_components:
            issues.append({"severity": "high", "issue": "Missing provenance components", "recommendation": "Attach native/plugin component provenance before final output."})
        if not disclosures:
            issues.append({"severity": "high", "issue": "Missing third-party/native disclosure", "recommendation": "Add disclosure text to the output manifest."})
        if plugin_components and output_mode == "native_inhouse":
            issues.append({"severity": "critical", "issue": "Plugin output cannot be marked fully native", "recommendation": "Use hybrid/plugin mode and disclose plugin usage."})
        claimed_mode = package.get("claimed_output_mode") or manifest.get("claimed_output_mode")
        if plugin_components and claimed_mode == "native_inhouse":
            issues.append({"severity": "critical", "issue": "False native claim detected while plugin components are present", "recommendation": "Mark output as hybrid/plugin and disclose third-party usage."})
        if plugin_components and not _mentions_plugin_disclosure(disclosures):
            issues.append({"severity": "high", "issue": "Plugin usage lacks explicit disclosure", "recommendation": "Mention third-party/plugin/open-source use and license boundaries."})

        route = package.get("route", {})
        if plugin_components and route.get("reason", "").lower().find("native-first") >= 0 and route.get("plugin_allowed") is False:
            issues.append({"severity": "medium", "issue": "Route metadata says plugin disallowed but plugins are recorded", "recommendation": "Correct route metadata or plugin provenance."})

        passed = not any(item["severity"] in {"critical", "high"} for item in issues)
        report = {
            "project_id": project_id,
            "gate": "credibility",
            "passed": passed,
            "output_mode": output_mode,
            "native_components": native_components,
            "plugin_components": plugin_components,
            "disclosures": disclosures,
            "issues": issues,
            "created_at": now_utc(),
        }
        report["report_path"] = save_gate_report(project_id, "credibility_report", report)
        return report

    @staticmethod
    def classify_output_mode(native_components: list, plugin_components: list) -> str:
        if native_components and plugin_components:
            return "hybrid"
        if plugin_components:
            return "plugin"
        return "native_inhouse"


def _mentions_plugin_disclosure(disclosures: list[str]) -> bool:
    text = " ".join(str(item).lower() for item in disclosures)
    return any(token in text for token in ("plugin", "third-party", "third party", "open-source", "license"))
