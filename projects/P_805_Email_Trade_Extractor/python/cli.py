"""P_805 command-line entry point.

Phase 1 (scan only — what's in each mbox, who's approved, who's not):
    python cli.py
    python cli.py --account icloud

Phase 3 (scan + ticker extraction → daily CSV):
    python cli.py --phase 3
    python cli.py --phase 3 --account icloud

Phase 5.3 (move successfully-extracted messages via IMAP; defaults to
config.MOVE_DRY_RUN=True until flipped):
    python cli.py --phase 53

IMAP auth check (connect+login+logout only, no search/move; safe any time):
    python cli.py --check-imap-auth
    python cli.py --check-imap-auth --account gmail

Outlook OAuth2 one-time browser login (run this yourself, once, before
using outlook with --phase 53 or --check-imap-auth --account outlook):
    python cli.py --outlook-oauth-login

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
from application.phase53_move import run as run_phase53  # noqa: E402
from application.imap_auth_check import run as run_imap_auth_check  # noqa: E402
from application.p805_kb_writer import scan_kb_inbox  # noqa: E402
from application.outlook_oauth_login import run as run_outlook_oauth_login  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse --phase, --account, --kb-mode, and --kb-lookback flags."""
    parser = argparse.ArgumentParser(description="P_805 mbox scanner / extractor / KB writer")
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 3, 4, 35, 53],
        default=1,
        help="1 = scan + sender filter (default). 3 = extraction. 35 = LLM direction enrichment. 4 = consensus ranking. 53 = IMAP move to ExtractedNewsletterFolder.",
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
    parser.add_argument(
        "--check-imap-auth",
        action="store_true",
        help="Connect+login+logout to verify IMAP credentials only. No search, no move.",
    )
    parser.add_argument(
        "--outlook-oauth-login",
        action="store_true",
        help="One-time interactive browser login for Outlook OAuth2. Run this yourself, once.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.outlook_oauth_login:
        run_outlook_oauth_login()
    elif args.check_imap_auth:
        run_imap_auth_check(account=args.account)
    elif args.kb_mode:
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
    elif args.phase == 53:
        run_phase53()
