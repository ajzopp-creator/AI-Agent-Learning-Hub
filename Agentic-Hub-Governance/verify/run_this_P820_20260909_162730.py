"""
run_this_P820_20260909_162730.py
Add P_210 to P_820_SYSTEM_DOCUMENTATION.md routing table (6 targeted edits).
Backup already taken: P_820_SYSTEM_DOCUMENTATION.md.backup_2026-09-09
"""
import sys
import traceback
from pathlib import Path
from datetime import datetime

DOC_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_820_OrderSignalCapture"
    r"\docs\P_820_SYSTEM_DOCUMENTATION.md"
)
SCRIPT_PATH = Path(__file__)
DONE_PATH = Path(str(SCRIPT_PATH) + ".done")


def write_done(status, exit_code):
    DONE_PATH.write_text(
        f"status: {status}\nexit_code: {exit_code}\ntimestamp: {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


EDITS = [
    (
        "header version/date",
        "**Version:** 1.2\n**Created:** 2026-08-16\n**Last Updated:** 2026-09-06\n",
        "**Version:** 1.3\n**Created:** 2026-08-16\n**Last Updated:** 2026-09-09\n",
    ),
    (
        "Section 2.1 MUST bullet",
        "- Route P_116/SNT to P_820 directly -- no P_115 involvement needed\n"
        "  just to get a trade logged\n",
        "- Route P_116/SNT to P_820 directly -- no P_115 involvement needed\n"
        "  just to get a trade logged\n"
        "- Route P_210 (One Click Trading 2PM Income Trade) to P_820\n"
        "  directly, same as P_116/SNT -- write end-of-day after the\n"
        "  position resolves, not at entry, since it's a same-day-expiry\n"
        "  credit spread (added 2026-09-09)\n",
    ),
    (
        "Section 4 routing table",
        "| SNT | **No, never** | Pure subscription alert -- one option/week, "
        "pre-set stop+target, closes Friday. |\n",
        "| SNT | **No, never** | Pure subscription alert -- one option/week, "
        "pre-set stop+target, closes Friday. |\n"
        "| P_210 (One Click Trading 2PM Income Trade) | **No, never** | Pure "
        "subscription alert -- daily 2PM Telegram credit-spread signal (NDX "
        "verticals), pre-set structure, same-day expiry. Logged end-of-day "
        "after the position resolves (entry, any roll, and outcome all known "
        "by close), not at entry time like the swing sources. Added "
        "2026-09-09. |\n",
    ),
    (
        "Workflow 6.1 decision gate",
        "If source is P_116/SNT                --> log to P_820 directly, "
        "no P_115 step\n",
        "If source is P_116/SNT                --> log to P_820 directly, "
        "no P_115 step\n"
        "If source is P_210                     --> log to P_820 directly, "
        "no P_115 step; write end-of-day after the position resolves, not "
        "at entry (same-day expiry)\n",
    ),
    (
        "Section 8 session log",
        "| 2026-09-06 | P_117 routing correction (P_805 session) | Tony "
        "corrected the 2026-08-16 P_117 rule: newsletter/P_805-sourced picks "
        "go through P_115 evaluation by default (SignalSource=P_117 in "
        "tracker); P_820 is the exception, used only when a pick is "
        "convincing enough on its own to skip evaluation. Judgment call per "
        "signal, not a fixed split. Section 4 table, Section 2.1 Musts, and "
        "Workflow 6.1 decision gate all updated same session (imperative "
        "sweep). P_116/SNT rows unchanged. |\n",
        "| 2026-09-06 | P_117 routing correction (P_805 session) | Tony "
        "corrected the 2026-08-16 P_117 rule: newsletter/P_805-sourced picks "
        "go through P_115 evaluation by default (SignalSource=P_117 in "
        "tracker); P_820 is the exception, used only when a pick is "
        "convincing enough on its own to skip evaluation. Judgment call per "
        "signal, not a fixed split. Section 4 table, Section 2.1 Musts, and "
        "Workflow 6.1 decision gate all updated same session (imperative "
        "sweep). P_116/SNT rows unchanged. |\n"
        "| 2026-09-09 | P_210 source added (chat dictation session) | New "
        "subscription source, P_210 (One Click Trading 2PM Income Trade, "
        "publisher Graham Lindman/48bytesNorth via Telegram) -- daily NDX "
        "credit-spread signal, same-day expiry. Routed straight to P_820 "
        "like SNT, no P_115 involvement. Tony confirmed the timing rule: "
        "since entry/roll/outcome all resolve same day, write at end-of-day "
        "after close rather than at entry (differs from P_115/P_116 swing "
        "sources, which need entry-time capture). Two backfilled signals "
        "logged same session: NDX call credit spread 2026-09-04 (opened "
        "29520/29530 @.95, rolled to 29520/29540 @2.05 total credit, expired "
        "ITM, realized loss ~-1795) and NDX put credit spread 2026-09-09 "
        "(29370/29360 @1.15 credit, expired OTM near max profit). Section "
        "2.1 Musts, Section 4 table, and Workflow 6.1 decision gate all "
        "updated same session. |\n",
    ),
    (
        "footer",
        "*End of P_820 SYSTEM DOCUMENTATION v1.2 -- 2026-09-06*",
        "*End of P_820 SYSTEM DOCUMENTATION v1.3 -- 2026-09-09*",
    ),
]


def main():
    text = DOC_PATH.read_text(encoding="utf-8")
    for label, old, new in EDITS:
        count = text.count(old)
        if count != 1:
            raise ValueError(f"Edit '{label}': expected 1 occurrence, found {count}")
        text = text.replace(old, new, 1)
    DOC_PATH.write_text(text, encoding="utf-8")
    print("All 6 edits applied.")
    return True


if __name__ == "__main__":
    try:
        ok = main()
    except Exception:
        traceback.print_exc()
        ok = False

    if ok:
        print("PASS")
        write_done("PASS", 0)
        sys.exit(0)
    else:
        print("FAIL")
        write_done("FAIL", 1)
        sys.exit(1)
