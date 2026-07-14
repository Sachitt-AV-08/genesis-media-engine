from __future__ import annotations

from .benchmark_gate import BenchmarkGate
from .credibility_gate import CredibilityGate
from .reporting import now_utc, project_id_from, save_gate_report
from .security_gate import SecurityGate


class FinalOutputGate:
    def __init__(self, benchmark_threshold: int = 75) -> None:
        self.credibility_gate = CredibilityGate()
        self.benchmark_gate = BenchmarkGate(benchmark_threshold)
        self.security_gate = SecurityGate()

    def evaluate(self, render_result: dict) -> dict:
        project_id = project_id_from(render_result)
        credibility = self.credibility_gate.evaluate(render_result)
        benchmark = self.benchmark_gate.evaluate(render_result)
        security = self.security_gate.evaluate(render_result)
        final_passed = credibility["passed"] and security["passed"] and benchmark["passed"]
        report = {
            "project_id": project_id,
            "gate": "final_output",
            "passed": final_passed,
            "valid_final_output": final_passed,
            "credibility_gate": credibility,
            "benchmark_gate": benchmark,
            "security_gate": security,
            "created_at": now_utc(),
        }
        report["report_path"] = save_gate_report(project_id, "final_output_gate_report", report)
        return report
