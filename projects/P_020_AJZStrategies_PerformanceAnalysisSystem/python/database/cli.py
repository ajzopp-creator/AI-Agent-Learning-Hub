"""P_020 CLI entry point (WO-P020-E1.010).

Commands (run from python\\database\\ dir, p140 env):

    python cli.py auth --project ALL     -- ONE login, all projects (standard)
    python cli.py auth --project P_020   -- (re)issue P_020's own Schwab token
    python cli.py auth --project P_400   -- (re)issue P_400's Schwab token

ALL is the standard weekly path. Schwab revokes at the app-registration
level, so two separate logins leave only the most recent project working
(confirmed 2026-08-09). Single-project mode is retained for targeted
reauth, but running it re-grants and therefore kills the other projects'
tokens -- follow it with ALL, or just use ALL.

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
        choices=["ALL", "P_020", "P_400"],
        help="Which project's token to (re)issue; ALL = one login for every project",
    )

    args = parser.parse_args()

    if args.cmd == "auth":
        if args.project == "ALL":
            from application.schwab_auth_commands import cmd_auth_all

            return cmd_auth_all()

        from application.schwab_auth_commands import cmd_auth

        return cmd_auth(args.project)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
