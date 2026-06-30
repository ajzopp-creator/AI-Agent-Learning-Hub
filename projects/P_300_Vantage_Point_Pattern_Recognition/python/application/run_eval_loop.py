"""
FILE: run_eval_loop.py
VERSION: 1.1
DATE: 2026-06-28
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Orchestrates the Stage 6 walk-forward eval loop. Pure call
    sequence -- no business logic, no direct I/O, no catalog writes.
    Application purity (python-project-architecture SKILL): this
    module calls infrastructure/eval_io.py and domain/eval_scoring.py
    in order and nothing else.

        eval_io.load_full_catalog()
              -> (catalog_path, metadata, windows, labels)
        eval_scoring.run_walk_forward(catalog_path, metadata, windows,
                                       labels, threshold_overrides)
              -> WalkForwardBatch
        eval_io.write_walk_forward_report(batch)
              -> Path

    --buy-min-z (v1.1): optional CLI flag building a ThresholdOverrides
    with only buy_min_z_score set, for BUY_MIN_Z_SCORE comparison runs
    against the post-N=300-ablation backlog item. No other override
    field is exposed via CLI yet -- add as needed, same pattern.
    Production config.py / signal_classifier.py are never touched;
    the override only affects domain/eval_scoring.py's own gate copy.

    Run via run_eval_loop.bat in Tony's terminal (p140), NOT via
    windows-mcp:PowerShell (M-030 -- subprocess timeout wedges the
    MCP session). Read-only against the catalog throughout (M-017).

CHANGELOG:
    - 2026-06-28 v1.1: Added --buy-min-z CLI flag -> ThresholdOverrides,
      threaded through run_walk_forward. Summary line now states which
      gate (default or override value) produced the report.
    - 2026-06-28 v1.0: Initial release. Stage 6 eval loop file #4 of 5.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# sys.path bootstrap for direct invocation.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain.eval_scoring import run_walk_forward  # noqa: E402
from infrastructure.eval_io import (  # noqa: E402
    load_full_catalog, write_walk_forward_report,
)
from schemas_eval import ThresholdOverrides  # noqa: E402


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="P_300 Stage 6 walk-forward eval loop.",
    )
    parser.add_argument(
        "--buy-min-z", type=float, default=None,
        help=(
            "Override BUY_MIN_Z_SCORE for this run only (config.py "
            "default used when omitted). Does not modify config.py."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the full walk-forward eval loop end to end; print summary."""
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    overrides = (
        ThresholdOverrides(buy_min_z_score=args.buy_min_z)
        if args.buy_min_z is not None else None
    )

    catalog_path, metadata, windows, labels = load_full_catalog()
    batch = run_walk_forward(catalog_path, metadata, windows, labels, overrides)
    out_path = write_walk_forward_report(batch)

    n_buy = sum(1 for r in batch.results if r.signal_class.value == "BUY")
    n_watch = sum(1 for r in batch.results if r.signal_class.value == "WATCH")
    n_pass = sum(1 for r in batch.results if r.signal_class.value == "PASS")
    gate_label = (
        "config.py default" if overrides is None
        else f"buy_min_z_score={args.buy_min_z}"
    )

    print("P_300 Walk-Forward Eval Loop")
    print(f"Catalog:        {Path(catalog_path).name}")
    print(f"Gate:           {gate_label}")
    print(f"Patterns:       {batch.n_patterns}")
    print(f"Degenerate:     {batch.n_degenerate} (corpus_size == 0)")
    print(f"Signal counts:  BUY={n_buy} WATCH={n_watch} PASS={n_pass}")
    print(f"Report written: {out_path}")
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
