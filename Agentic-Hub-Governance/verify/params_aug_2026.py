"""P_000 Account Parameters -- August 2026 monthly update.

Balance from live Schwab pull 2026-08-04: Net Liq $31,348.39.
Dry-run by default. Pass --commit to write.
Updates all 5 synchronized locations + history row + change log.
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

FILE = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
            r"\P_000_PythonClaudeLocalLLM\config"
            r"\P_000_Account_Parameters_Current.md")
STAMP = "2026-08-04"
BALANCE = Decimal("31348.39")


def money(d):
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt(d):
    return f"{money(d):,.2f}"


RISK = money(BALANCE * Decimal("0.015"))
MAXP = money(BALANCE * Decimal("0.05"))
RISK_50, MAXP_50 = money(RISK / 2), money(MAXP / 2)
RISK_75 = money(RISK * Decimal("0.75"))
MAXP_75 = money(MAXP * Decimal("0.75"))

B, R, M = fmt(BALANCE), fmt(RISK), fmt(MAXP)

EDITS = [
    ("header dates",
     "**Last Updated:** July 01, 2026\n"
     "**Next Review:** August 2026 (monthly) or when balance hits $35,000",
     "**Last Updated:** August 04, 2026\n"
     "**Next Review:** September 2026 (monthly) or when balance hits $35,000"),

    ("active parameters",
     "| Account Balance | $32,072.00 |\n"
     "| Risk per Trade | 1.5% = $481.08|\n"
     "| Max Position (5%) | $1,603.60 |",
     f"| Account Balance | ${B} |\n"
     f"| Risk per Trade | 1.5% = ${R}|\n"
     f"| Max Position (5%) | ${M} |"),

    ("risk mode table",
     "| OFF / CORRECTION | $240.54 (50%) | $801.80 (50%) | avg_posture < -1.0 |\n"
     "| HALF | $360.81 (75%) | $1,202.70 (75%) | 25% reduction |\n"
     "| STANDARD | $481.08 | $1,603.60 | Base risk |\n"
     "| FULL | $481.08 | $1,603.60 | Same as STANDARD |\n"
     "| HOT | Tiered up to 5% | Up to $1,603.60 | avg_posture > 1.08 |",
     f"| OFF / CORRECTION | ${fmt(RISK_50)} (50%) | ${fmt(MAXP_50)} (50%) | avg_posture < -1.0 |\n"
     f"| HALF | ${fmt(RISK_75)} (75%) | ${fmt(MAXP_75)} (75%) | 25% reduction |\n"
     f"| STANDARD | ${R} | ${M} | Base risk |\n"
     f"| FULL | ${R} | ${M} | Same as STANDARD |\n"
     f"| HOT | Tiered up to 5% | Up to ${M} | avg_posture > 1.08 |"),

    ("three-gate block",
     "Gate 1 (Risk-Based):    $481.08 / (Entry - Stop)",
     f"Gate 1 (Risk-Based):    ${R} / (Entry - Stop)"),

    ("three-gate concentration",
     "Gate 3 (Concentration): $1,603.60 max (or premium for options)",
     f"Gate 3 (Concentration): ${M} max (or premium for options)"),

    ("growth current row",
     "| $32,072.00 (current) | $481.08 | $1,603.60 |",
     f"| ${B} (current) | ${R} | ${M} |"),

    ("history row",
     "| July 1, 2026 | $32,072.00 | $481.08 | $1,603.60 | Monthly review -- Net Liq per broker |",
     "| July 1, 2026 | $32,072.00 | $481.08 | $1,603.60 | Monthly review -- Net Liq per broker |\n"
     f"| Aug 4, 2026 | ${B} | ${R} | ${M} | Monthly review -- Net Liq per broker (live pull) |"),

    ("change log",
     "- July 1, 2026 - Updated Account Balance to $32,072.00 (Net Liq per broker); "
     "synced derived tables to base $481.08 / $1,603.60 (Risk Mode Adjustments, "
     "Three-Gate block, Growth current row); Next Review moved to August 2026",
     "- July 1, 2026 - Updated Account Balance to $32,072.00 (Net Liq per broker); "
     "synced derived tables to base $481.08 / $1,603.60 (Risk Mode Adjustments, "
     "Three-Gate block, Growth current row); Next Review moved to August 2026\n"
     f"- August 4, 2026 - Updated Account Balance to ${B} (Net Liq per broker, live "
     f"Schwab pull); synced derived tables to base ${R} / ${M} (Risk Mode Adjustments, "
     "Three-Gate block, Growth current row); Next Review moved to September 2026. "
     "Buying Power / Cash Available auto-written by the same pull per WO-P020-E1.009."),
]


def load():
    raw = FILE.read_bytes()
    for enc in ("utf-8", "cp1252"):
        try:
            d = raw.decode(enc)
            return d.replace("\r\n", "\n"), enc, b"\r\n" in raw
        except UnicodeDecodeError:
            continue
    raise SystemExit("Could not decode file")


def main():
    commit = "--commit" in sys.argv
    out = [f"P_000 params update  |  MODE: {'COMMIT' if commit else 'DRY-RUN'}"]
    out.append(f"  balance ${B}  risk ${R}  max ${M}")

    if not FILE.exists():
        out.append(f"MISSING: {FILE}")
        print("\n".join(out))
        return 1

    text, enc, crlf = load()
    out.append(f"  encoding: {enc}\n")
    ok = True

    for label, old, new in EDITS:
        n = text.count(old)
        out.append(f"  {label}: {n} match(es)")
        if n != 1:
            out.append(f"  !! ABORT -- expected exactly 1 for {label}")
            ok = False
        else:
            text = text.replace(old, new, 1)

    if not ok:
        out.append("\nRESULT: ABORTED -- nothing written.")
        print("\n".join(out))
        return 1

    if commit:
        bak = FILE.with_name(f"{FILE.stem}_backup_{STAMP}{FILE.suffix}")
        bak.write_bytes(FILE.read_bytes())
        body = text.replace("\n", "\r\n") if crlf else text
        FILE.write_bytes(body.encode(enc))
        out.append(f"\n  wrote {FILE.name}  (backup: {bak.name})")
        out.append("RESULT: COMMITTED")
    else:
        out.append(f"\nRESULT: DRY-RUN OK -- all {len(EDITS)} anchors matched.")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
