"""P_020 CLI entry point (WO-P020-E1.010).

Commands (run from python\\database\\ dir, p140 env):

    python cli.py auth                   -- ONE login, all projects (default, standard)
    python cli.py auth --project ALL     -- same as above, explicit
    python cli.py auth --project P_020   -- (re)issue P_020's own Schwab token
    python cli.py auth --project P_400   -- (re)issue P_400's Schwab token
    python cli.py reconcile --account AJZ --start 2026-08-01 --end 2026-09-07
                                          -- reconcile open P_400 LIVE orders (WO-P400-E6.001)
    python cli.py reconcile --paper --statement <path to Account Statement CSV>
                                          -- reconcile open P_400 PAPER orders (WO-P400-E6.001)

ALL is the standard weekly path, and now the default if --project is
omitted entirely. Schwab revokes at the app-registration level, so two
separate logins leave only the most recent project working (confirmed
2026-08-09). Single-project mode is retained for targeted reauth, but
running it re-grants and therefore kills the other projects' tokens --
follow it with ALL, or just use ALL.

Note (2026-08-18): ALL-mode propagation does not by itself guarantee a
project's token survives a week -- see WO-P020-E1.010's OPEN section and
2026-08-18 Occurrence Log entry. A routine, non-login token refresh by one
project appears able to invalidate the shared copy in another project's
file. This default only prevents accidental single-project logins; it does
not address that separate, confirmed-live finding.

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
        default="ALL",
        choices=["ALL", "P_020", "P_400"],
        help="Which project's token to (re)issue; ALL = one login for every "
             "project (default if omitted)",
    )

    p_reconcile = sub.add_parser(
        "reconcile", help="Reconcile open P_400 orders against Schwab or a paper statement (WO-P400-E6.001)"
    )
    p_reconcile.add_argument(
        "--account", default="AJZ", help="Account key, e.g. AJZ, IRA (default AJZ) -- live path only"
    )
    p_reconcile.add_argument(
        "--start", default=None, help="ISO start datetime for the Schwab orders pull -- live path only"
    )
    p_reconcile.add_argument(
        "--end", default=None, help="ISO end datetime for the Schwab orders pull -- live path only"
    )
    p_reconcile.add_argument(
        "--paper", action="store_true",
        help="Reconcile PAPER orders against a statement file instead of a live Schwab pull",
    )
    p_reconcile.add_argument(
        "--statement", default=None,
        help="Path to a raw TOS/paperMoney Account Statement CSV -- required with --paper",
    )

    args = parser.parse_args()

    if args.cmd == "auth":
        if args.project == "ALL":
            from application.schwab_auth_commands import cmd_auth_all

            return cmd_auth_all()

        from application.schwab_auth_commands import cmd_auth

        return cmd_auth(args.project)

    if args.cmd == "reconcile":
        from application.reconcile_command import run_reconcile_command

        run_reconcile_command(
            args.account, args.start, args.end,
            paper=args.paper, statement=args.statement,
        )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
