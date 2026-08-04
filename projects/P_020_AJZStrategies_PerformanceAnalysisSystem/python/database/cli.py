"""P_020 CLI entry point (WO-P020-E1.010).

Commands (run from python\\database\\ dir, p140 env):

    python cli.py auth --project P_020   -- (re)issue P_020's own Schwab token
    python cli.py auth --project P_400   -- (re)issue P_400's Schwab token

Command implementations live in application/ -- this file is argparse
wiring + main() dispatch only.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(prog="cli.py")
    sub = parser.add_subparsers(dest="cmd")

    p_auth = sub.add_parser("auth", help="Run Schwab OAuth login for a project")
    p_auth.add_argument(
        "--project",
        required=True,
        choices=["P_020", "P_400"],
        help="Which project's token to (re)issue",
    )

    args = parser.parse_args()

    if args.cmd == "auth":
        from application.schwab_auth_commands import cmd_auth

        return cmd_auth(args.project)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
