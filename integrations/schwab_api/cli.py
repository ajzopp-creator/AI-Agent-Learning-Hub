# cli.py
# AI-Agent-Learning-Hub — Schwab API Integration
# Command-line entry point

import logging
import sys

from auth_workflow import run_initial_auth, run_token_check, run_connection_test

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)

COMMANDS = {
    "auth"  : ("Run OAuth login flow (one-time setup)",  run_initial_auth),
    "check" : ("Check token status, refresh if needed",  run_token_check),
    "test"  : ("Test live Schwab API connection",         run_connection_test),
}


def print_usage() -> None:
    """Print available commands."""
    print("\nSchwab API - Usage:")
    print("  python cli.py <command>\n")
    print("Commands:")
    for cmd, (desc, _) in COMMANDS.items():
        print(f"  {cmd:<10} {desc}")
    print()


def main() -> None:
    """Parse command and dispatch to correct workflow."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    command = sys.argv[1].lower()
    if command not in COMMANDS:
        print(f"\n[FAIL] Unknown command: '{command}'")
        print_usage()
        sys.exit(1)
    _, workflow_fn = COMMANDS[command]
    success = workflow_fn()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
