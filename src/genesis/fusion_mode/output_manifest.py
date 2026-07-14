from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json


@dataclass
class ProvenanceManifest:
    project_id: str
    mode: str
    native_components: list[str]
    plugin_components: list[str]
    disclosures: list[str]
    outputs: dict
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class ManifestStore:
    def __init__(self, root: str | Path = "reports/genesis") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, manifest: ProvenanceManifest) -> dict:
        path = self.root / f"{manifest.project_id}_manifest.json"
        path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
        return manifest.to_dict()

    def get(self, project_id: str) -> dict:
        path = self.root / f"{project_id}_manifest.json"
        if not path.exists():
            return {"found": False, "project_id": project_id}
        return {"found": True, "manifest": json.loads(path.read_text(encoding="utf-8"))}


manifest_store = ManifestStore()


class OutputManifestBuilder:
    def save(self, package: dict) -> dict:
        provenance = package.get("provenance", {})
        manifest = ProvenanceManifest(
            project_id=package["project_id"],
            mode="fusion",
            native_components=provenance.get("native_components", []),
            plugin_components=provenance.get("plugin_components", []),
            disclosures=provenance.get("disclosures", []),
            outputs={"scene": package.get("scene"), "hybrid_render_plan": package.get("hybrid_render_plan"), "quality_gate": package.get("quality_gate")},
        )
        return manifest_store.save(manifest)
