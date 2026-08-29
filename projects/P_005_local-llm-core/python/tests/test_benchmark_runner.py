"""Regression tests for application/benchmark_runner markdown logging."""

from pathlib import Path
from application.benchmark_runner import BenchmarkRunner
from schemas import BenchmarkMetrics, TestCaseResult


def test_record_benchmark_to_markdown(tmp_path: Path) -> None:
    """Ensure benchmark records append correctly formatted markdown tables."""
    log_file = tmp_path / "BENCHMARKS.md"
    runner = BenchmarkRunner()

    metrics = BenchmarkMetrics(
        ttft_ms=350.25,
        total_duration_sec=2.15,
        tokens_generated=95,
        tokens_per_sec=44.18,
    )
    cases = [
        TestCaseResult(
            case_id="TC_01_TEST",
            passed=True,
            latency_sec=1.12,
            output_preview="Calculation verified successfully.",
        )
    ]

    target = runner.record_benchmark_to_markdown(metrics, cases, log_path=log_file)
    assert target.exists()

    content = target.read_text(encoding="utf-8")
    assert "Raw Inference Performance" in content
    assert "44.18 tokens/sec" in content
    assert "TC_01_TEST" in content
    assert "PASS" in content