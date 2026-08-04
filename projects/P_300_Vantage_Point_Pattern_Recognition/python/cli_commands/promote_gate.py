"""
FILE: cli_commands/promote_gate.py
VERSION: 1.0
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    `promote-gate` -- WO-P300-E5.005. Compares the current run's
    staging walk-forward report against its baseline and decides
    whether the batch is safe to promote automatically.

    DECIDES ONLY. This command never writes to a catalog. It reads two
    reports, evaluates, prints, manages the marker file, and signals
    via exit code. The actual promote stays where it already is
    (`ingest-mined --promote`), so there is exactly one code path that
    mutates the live catalog.

    EXIT CODES -- the PS1 launcher branches on these:
        0  PROMOTE  -- deltas within bounds; caller may promote
        2  STOP     -- a delta breached; caller must NOT promote
        1  ERROR    -- could not evaluate (bad pair, parse failure)

    2 rather than 1 for STOP is deliberate. A STOP is a successful
    evaluation with a negative answer; an ERROR means no answer was
    reached. Collapsing them would let a crashed parse read as a
    quality failure, sending the operator to inspect a batch that is
    probably fine.

    MARKER SIDE EFFECTS (see infrastructure/promote_marker_io.py):
        clean PROMOTE  -> clears any stale marker
        waived PROMOTE -> writes a WAIVED (informational) marker
        STOP           -> writes a STOP (action-required) marker

CHANGELOG:
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import MODELS_DIR, PROJECT_ROOT
from domain.promote_gate import evaluate_promote_gate
from infrastructure.eval_io import EVAL_REPORTS_DIR
from infrastructure.promote_marker_io import (
    build_marker, clear_marker, write_marker,
)
from infrastructure.walkforward_report_io import (
    find_report_pair, parse_walkforward_report,
)
from schemas_promote_gate import GateThresholds, PromoteGateVerdict

EXIT_PROMOTE = 0
EXIT_ERROR = 1
EXIT_STOP = 2


def _print_verdict(verdict: PromoteGateVerdict) -> None:
    bar = "=" * 70
    print(f"\n{bar}\n PROMOTE GATE -- {verdict.decision}\n{bar}")
    for line in verdict.reasons:
        print(f"  {line}")
    print(f"\n  baseline: {Path(verdict.pre.source_path).name}")
    print(f"  staging:  {Path(verdict.staging.source_path).name}")
    print(bar)


def _handle_marker(verdict: PromoteGateVerdict, staging_db: Path) -> None:
    marker = build_marker(verdict, staging_db)
    if marker is None:
        if clear_marker(PROJECT_ROOT):
            print("  marker: cleared a stale marker from a prior run.")
        else:
            print("  marker: none needed (clean pass).")
        return
    path = write_marker(PROJECT_ROOT, marker)
    print(f"  marker: {marker.severity} written -> {path}")
    print(f"  INIT Step 0.6 will surface this at your next session start.")


def _cmd_promote_gate(args: argparse.Namespace) -> int:
    thresholds = GateThresholds(
        max_buy_precision_drop_pp=args.buy_drop_pp,
        max_pass_accuracy_drop_pp=args.pass_drop_pp,
        min_buy_n=args.min_buy_n,
    )
    try:
        if args.baseline and args.staging:
            baseline, staging = Path(args.baseline), Path(args.staging)
        else:
            baseline, staging = find_report_pair(
                Path(args.eval_dir or EVAL_REPORTS_DIR),
                max_age_minutes=args.max_pair_age_minutes,
            )
        verdict = evaluate_promote_gate(
            parse_walkforward_report(baseline),
            parse_walkforward_report(staging),
            thresholds,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"\nPROMOTE GATE ERROR -- could not evaluate: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        print("No verdict reached. This is NOT a quality failure -- the "
              "batch was never assessed.", file=sys.stderr)
        return EXIT_ERROR

    _print_verdict(verdict)
    _handle_marker(verdict, Path(args.staging_db))
    return EXIT_PROMOTE if verdict.decision == "PROMOTE" else EXIT_STOP


def register(subparsers: argparse._SubParsersAction) -> None:
    """Registers promote-gate."""
    p = subparsers.add_parser(
        "promote-gate",
        help="WO-P300-E5.005: compare staging vs baseline walk-forward "
             "reports and decide whether the batch is safe to promote. "
             "Exit 0=promote, 2=stop, 1=error. Never writes a catalog.",
    )
    p.add_argument(
        "--eval-dir", default=None,
        help="Walk-forward report dir; defaults to eval_io.EVAL_REPORTS_DIR.",
    )
    p.add_argument(
        "--baseline", default=None,
        help="Explicit baseline report path. Must be paired with --staging; "
             "bypasses auto-discovery AND its staleness check.",
    )
    p.add_argument(
        "--staging", default=None,
        help="Explicit staging report path. Must be paired with --baseline.",
    )
    p.add_argument(
        "--staging-db", default=str(MODELS_DIR / "staging_ingest_mined.db"),
        help="Staging DB recorded in the marker as the file at risk.",
    )
    p.add_argument(
        "--buy-drop-pp", type=float, default=3.0,
        help="Max tolerated BUY precision drop in pp (inclusive). "
             "Operator-confirmed default 3.0.",
    )
    p.add_argument(
        "--pass-drop-pp", type=float, default=3.0,
        help="Max tolerated PASS accuracy drop in pp (inclusive).",
    )
    p.add_argument(
        "--min-buy-n", type=int, default=400,
        help="Below this staging n, the comparison is waived as untestable "
             "rather than failed -- a 3pp bar is inside sampling noise.",
    )
    p.add_argument(
        "--max-pair-age-minutes", type=int, default=720,
        help="Reject a baseline/staging pair further apart than this; "
             "guards against pairing with a stale baseline report.",
    )
    p.set_defaults(func=_cmd_promote_gate)
