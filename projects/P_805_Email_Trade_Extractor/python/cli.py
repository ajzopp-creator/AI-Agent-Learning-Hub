"""P_805 command-line entry point.

Phase 1 (scan only — what's in each mbox, who's approved, who's not):
    python cli.py
    python cli.py --account icloud

Phase 3 (scan + ticker extraction → daily CSV):
    python cli.py --phase 3
    python cli.py --phase 3 --account icloud

This file adds its own directory (python/) to sys.path at startup so
that sibling modules (config, domain/, infrastructure/, application/)
resolve with bare imports regardless of which directory you run from.
"""

import argparse
import sys
from pathlib import Path

# Make this file's directory (python/) importable before anything else loads.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
from application.phase1_scan import run as run_phase1  # noqa: E402
from application.phase3_extract import run as run_phase3  # noqa: E402
from application.phase4_rank import run as run_phase4  # noqa: E402
from application.phase35_enrich import run as run_phase35  # noqa: E402
from application.p805_kb_writer import scan_kb_inbox  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse --phase, --account, --kb-mode, and --kb-lookback flags."""
    parser = argparse.ArgumentParser(description="P_805 mbox scanner / extractor / KB writer")
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 3, 4, 35],
        default=1,
        help="1 = scan + sender filter (default). 3 = extraction. 35 = LLM direction enrichment. 4 = consensus ranking.",
    )
    parser.add_argument(
        "--account",
        choices=sorted(config.MBOX_FILES.keys()),
        default=None,
        help="Scan one account only. Default: all accounts in priority order.",
    )
    parser.add_argument(
        "--kb-mode",
        choices=["full", "summary"],
        default=None,
        help="KB write mode: 'full' (default) or 'summary'. If set, reads from data/inbox/ and writes to Obsidian.",
    )
    parser.add_argument(
        "--kb-lookback",
        type=int,
        default=7,
        help="KB email lookback window in days (default: 7).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.kb_mode:
        # KB write mode
        kb_mode = args.kb_mode if args.kb_mode else "full"
        scan_kb_inbox(kb_mode=kb_mode, kb_lookback_days=args.kb_lookback)
    elif args.phase == 1:
        run_phase1(account=args.account)
    elif args.phase == 3:
        run_phase3(account=args.account)
    elif args.phase == 35:
        run_phase35()
    elif args.phase == 4:
        run_phase4()
