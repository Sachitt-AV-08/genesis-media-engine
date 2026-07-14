from pathlib import Path

from genesis.gates.security_gate import SecurityGate
from genesis.gates.credibility_gate import CredibilityGate
from genesis.gates.benchmark_gate import BenchmarkGate
from genesis.gates.final_output_gate import FinalOutputGate


def _mock_render_result(output_path: str | None = None):
    return {
        "ok": True,
        "project_id": "gate_test",
        "output_path": output_path,
        "output_metadata": {"duration_seconds": 20, "aspect_ratio": "9:16", "storyboard_beats_matched": 2},
        "approved": True,
        "dependencies": {"can_render_video": True},
        "package": {
            "project_id": "gate_test",
            "scene": {"constraints": {"duration_seconds": 20, "aspect_ratio": "9:16"}},
            "storyboard": [{"shot": 1}, {"shot": 2}],
            "caption_plan": {"captions": [{"text": "Genesis OS"}, {"text": "Launch ready"}]},
            "veda_validation": {"approved": True},
            "manifest": {
                "native_components": ["Scene DSL", "validator"],
                "plugin_components": [],
                "disclosures": ["Clean-room native plan; no third-party model output claimed."],
            },
            "provenance": {
                "native_components": ["Scene DSL", "validator"],
                "plugin_components": [],
                "disclosures": ["Clean-room native plan; no third-party model output claimed."],
            },
        },
    }


class TestSecurityGate:
    def test_passes_safe_result(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        report = SecurityGate().evaluate(_mock_render_result("output/genesis/ok.mp4"))
        assert report["passed"] is True

    def test_blocks_secret_and_unapproved(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = _mock_render_result("output/genesis/ok.mp4")
        result["approved"] = False
        result["logs"] = ["token=abcdefghi123456789"]
        report = SecurityGate().evaluate(result)
        assert report["passed"] is False
        assert report["checks"]["execution_after_approval"] is False
        assert report["checks"]["no_secrets_in_logs"] is False

    def test_blocks_unsafe_output_folder(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = _mock_render_result("../outside.mp4")
        report = SecurityGate().evaluate(result)
        assert report["passed"] is False
        assert report["checks"]["safe_output_folder"] is False


class TestCredibilityGate:
    def test_passes_native_manifest(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        report = CredibilityGate().evaluate(_mock_render_result())
        assert report["passed"] is True
        assert report["output_mode"] == "native_inhouse"

    def test_blocks_false_native_plugin_claim(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = _mock_render_result()
        result["package"]["manifest"]["plugin_components"] = ["MoviePy"]
        result["package"]["manifest"]["disclosures"] = ["Plugin usage disclosed with MIT license boundary."]
        result["package"]["claimed_output_mode"] = "native_inhouse"
        report = CredibilityGate().evaluate(result)
        assert report["passed"] is False
        assert report["output_mode"] == "hybrid"


class TestBenchmarkGate:
    def test_scores_valid_output(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        output = Path("output/genesis/ok.mp4")
        output.parent.mkdir(parents=True)
        output.write_bytes(b"video")
        result = _mock_render_result(str(output))
        report = BenchmarkGate().evaluate(result)
        assert report["passed"] is True
        assert report["quality_score"] == 100

    def test_fails_missing_output_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = _mock_render_result("output/genesis/missing.mp4")
        report = BenchmarkGate().evaluate(result)
        assert report["passed"] is False
        assert report["checks"]["output_file_validity"] is False


class TestFinalOutputGate:
    def test_passes_only_when_all_gates_pass(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        output = Path("output/genesis/final.mp4")
        output.parent.mkdir(parents=True)
        output.write_bytes(b"video")
        result = _mock_render_result(str(output))
        report = FinalOutputGate().evaluate(result)
        assert report["passed"] is True
        assert report["valid_final_output"] is True

    def test_fails_when_benchmark_fails(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = _mock_render_result("output/genesis/missing.mp4")
        report = FinalOutputGate().evaluate(result)
        assert report["passed"] is False
        assert report["benchmark_gate"]["passed"] is False
