"""Application pipeline for measuring inference throughput and persisting benchmarks."""

from datetime import datetime
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

import config
from application.tool_orchestrator import ToolOrchestrator
from infrastructure.lms_client import LMStudioClient
from schemas import BenchmarkMetrics, TestCaseResult

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Coordinates execution of latency, speed, and accuracy test suites."""

    def __init__(
        self,
        client: Optional[LMStudioClient] = None,
        orchestrator: Optional[ToolOrchestrator] = None,
    ) -> None:
        """Initialize benchmark runner components."""
        self.client = client or LMStudioClient()
        self.orchestrator = orchestrator or ToolOrchestrator(client=self.client)

    def benchmark_raw_inference(self, prompt: Optional[str] = None) -> BenchmarkMetrics:
        """Measure Time To First Token (TTFT) and token generation speed.

        Args:
            prompt: Optional prompt override.

        Returns:
            Validated BenchmarkMetrics model.
        """
        test_prompt = prompt or config.DEFAULT_BENCHMARK_PROMPT
        messages = [{"role": "user", "content": test_prompt}]

        start_time = time.perf_counter()
        first_token_time: Optional[float] = None
        total_tokens = 0

        stream = self.client.chat_completion(messages=messages, stream=True, temperature=0.0)
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                total_tokens += 1

        end_time = time.perf_counter()
        ttft_ms = (first_token_time - start_time) * 1000 if first_token_time else 0.0
        total_duration = end_time - start_time
        tps = total_tokens / (end_time - first_token_time) if (first_token_time and end_time > first_token_time) else 0.0

        return BenchmarkMetrics(
            ttft_ms=round(ttft_ms, 2),
            total_duration_sec=round(total_duration, 2),
            tokens_generated=total_tokens,
            tokens_per_sec=round(tps, 2),
        )

    def run_tool_benchmarks(self) -> List[TestCaseResult]:
        """Evaluate accuracy and execution speed across core tool setups.

        Returns:
            List of TestCaseResult records.
        """
        eval_cases: List[Dict[str, Any]] = [
            {
                "id": "TC_01_MATH",
                "prompt": "Calculate the compound interest for principal 25000 at 0.08 interest for 3 years.",
            },
            {
                "id": "TC_02_FS_LIST",
                "prompt": "List the files and folders inside the directory 'docs'.",
            },
            {
                "id": "TC_03_SHELL",
                "prompt": "Run a powershell command to print 'P_005_PIPELINE_ACTIVE' to stdout.",
            },
        ]

        results: List[TestCaseResult] = []
        for case in eval_cases:
            t0 = time.perf_counter()
            try:
                output = self.orchestrator.run(case["prompt"], verbose=False)
                latency = round(time.perf_counter() - t0, 2)
                passed = len(output) > 0 and "ERROR" not in output
                results.append(
                    TestCaseResult(
                        case_id=case["id"],
                        passed=passed,
                        latency_sec=latency,
                        output_preview=output[:90].replace("\n", " ") + "...",
                    )
                )
            except Exception as err:
                results.append(
                    TestCaseResult(
                        case_id=case["id"],
                        passed=False,
                        latency_sec=round(time.perf_counter() - t0, 2),
                        output_preview=f"EXCEPTION: {str(err)}",
                    )
                )
        return results

    def record_benchmark_to_markdown(
        self,
        metrics: BenchmarkMetrics,
        tool_results: List[TestCaseResult],
        log_path: Optional[Path] = None,
    ) -> Path:
        """Format and append benchmark run to documentation markdown file.

        Args:
            metrics: Raw inference benchmark measurements.
            tool_results: Tool evaluation results list.
            log_path: Optional custom file destination.

        Returns:
            Resolved Path of the written markdown log.
        """
        target = log_path or config.BENCHMARK_LOG_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        model_name = self.client.app_cfg.model_defaults.model_alias

        entry_lines = [
            f"## Benchmark Run: `{model_name}` ({timestamp})",
            "",
            "### Raw Inference Performance",
            f"- **Time To First Token (TTFT):** {metrics.ttft_ms} ms",
            f"- **Generation Throughput:** {metrics.tokens_per_sec} tokens/sec",
            f"- **Tokens Generated:** {metrics.tokens_generated}",
            f"- **Total Duration:** {metrics.total_duration_sec} s",
            "",
            "### Tool Call Accuracies",
            "| Case ID | Status | Latency (s) | Output Preview |",
            "|---|---|---|---|",
        ]

        for r in tool_results:
            status_badge = "PASS" if r.passed else "FAIL"
            clean_preview = r.output_preview.replace("|", "\\|")
            entry_lines.append(f"| `{r.case_id}` | **{status_badge}** | {r.latency_sec}s | {clean_preview} |")

        entry_lines.append("\n---\n")
        content = "\n".join(entry_lines)

        with open(target, "a", encoding="utf-8") as f:
            f.write(content)

        logger.info("Benchmark logged to %s", target)
        return target