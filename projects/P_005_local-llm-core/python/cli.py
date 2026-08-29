"""Command-line interface entry point for P_005 Local LLM Core."""

import argparse
import logging
import sys

from application.benchmark_runner import BenchmarkRunner
from application.tool_orchestrator import ToolOrchestrator
from infrastructure.lms_client import LMStudioClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("P_005_CLI")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(description="P_005 Local LLM Core Management CLI")
    parser.add_argument("--smoke", action="store_true", help="Run server connectivity smoke test")
    parser.add_argument("--bench", action="store_true", help="Run throughput and tool benchmark suite")
    parser.add_argument("--chat", action="store_true", help="Start interactive agent REPL session")
    parser.add_argument("--prompt", type=str, default=None, help="Execute interactive tool prompt")
    return parser


def start_chat_repl(orchestrator: ToolOrchestrator) -> None:
    """Run an interactive console REPL for tool-driven conversations."""
    model_name = orchestrator.client.app_cfg.model_defaults.model_alias
    print("\n" + "=" * 65)
    print(f"P_005 INTERACTIVE AGENT REPL | Model: [{model_name}]")
    print("Type 'exit', 'quit', or 'q' to end session.")
    print("=" * 65 + "\n")

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nExiting session. Goodbye!")
                break

            response = orchestrator.run(user_input, verbose=False)
            print(f"\nAgent > {response}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Exiting.")
            break


def main() -> None:
    """Parse CLI arguments and dispatch execution."""
    parser = build_parser()
    args = parser.parse_args()
    client = LMStudioClient()

    if args.smoke:
        logger.info("Executing LM Studio connection smoke test...")
        messages = [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Respond with 'P_005_SYSTEM_ONLINE' to verify connection."},
        ]
        try:
            print("\nResponse: ", end="")
            for token in client.stream_response(messages):
                print(token, end="", flush=True)
            print("\n[OK] Smoke test successful.\n")
        except Exception as e:
            logger.error("Smoke test failed: %s", e)
            sys.exit(1)
        return

    if args.bench:
        runner = BenchmarkRunner(client=client)
        logger.info("Starting raw generation throughput benchmark...")
        metrics = runner.benchmark_raw_inference()
        print("\n" + "=" * 60)
        print(f"MODEL BENCHMARK: [{client.app_cfg.model_defaults.model_alias}]")
        print("=" * 60)
        print(f"  - TTFT:             {metrics.ttft_ms} ms")
        print(f"  - Generation Speed: {metrics.tokens_per_sec} tokens/sec")
        print(f"  - Total Elapsed:    {metrics.total_duration_sec} s")

        logger.info("Running tool accuracy benchmarks...")
        cases = runner.run_tool_benchmarks()
        print("\nTOOL ACCURACY TEST CASES:")
        for c in cases:
            tag = "[PASS]" if c.passed else "[FAIL]"
            print(f"  - {tag} {c.case_id} ({c.latency_sec}s): {c.output_preview}")

        # Persist benchmark log
        log_file = runner.record_benchmark_to_markdown(metrics, cases)
        print(f"\n[OK] Benchmark appended to: {log_file}")
        print("=" * 60 + "\n")
        return

    if args.chat:
        orchestrator = ToolOrchestrator(client=client)
        start_chat_repl(orchestrator)
        return

    if args.prompt:
        orchestrator = ToolOrchestrator(client=client)
        logger.info("Executing tool-orchestrated prompt: %s", args.prompt)
        output = orchestrator.run(args.prompt, verbose=True)
        print("\n" + "=" * 60)
        print("FINAL SYNTHESIZED OUTPUT:")
        print("=" * 60)
        print(output)
        print("=" * 60 + "\n")
        return

    parser.print_help()


if __name__ == "__main__":
    main()