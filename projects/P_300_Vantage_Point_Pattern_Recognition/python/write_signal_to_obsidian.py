#!/usr/bin/env python
"""Parse latest report and write signal to Obsidian vault via Hub interface.

FILE:        write_signal_to_obsidian.py
VERSION:     1.4
DATE:        2026-06-01
AUTHOR:      Anthony Zoppi / Claude
LAYER:       application (P_300 side -- calls Hub vault interface)
DESCRIPTION: Find latest .txt report for a symbol, parse signal fields,
             write normalized note to Obsidian vault via the Hub interface.
CHANGELOG:
  v1.4  2026-06-01  Removed 'date' and 'anchor_date' from trade_data payload.
                    P300Record v2.0 types both as Optional[date] (datetime.date),
                    which rejects plain strings in Pydantic v2 strict mode.
                    'date' is deprecated in Note Standard v2.0 -- drop it entirely.
                    'anchor_date' is not required by write_handler -- omit to avoid
                    coercion failure. signal_date carries the date semantics.
  v1.3  2026-06-01  Added signal_date and written_by fields to trade_data
                    per P_800 Note Standard v2.0 (work order 2026-06-01).
                    run_date and run_ts are injected by write_handler automatically.
  v1.2  2026-05-31  Replaced direct sys.path injection into P_800 internals
                    with the published Hub interface:
                    shared_resources/python_utils/vault_interface.write_to_vault().
                    Per M-038: always use the Hub interface for cross-project
                    calls -- never reach into another project's internals.
  v1.1  2026-05-31  Fixed double-division bug on h_win_rate (was wr/100,
                    report already stores decimal fraction) and h_mean_ret
                    (was float(mr.rstrip('%'))/100, rstrip was a no-op and
                    /100 produced wrong scale). Changed overwrite=False to
                    overwrite=True so re-runs update the existing note.
  v1.0  2026-05-30  Initial version.
"""

import sys
import re
from pathlib import Path
from datetime import datetime

# Hub interface -- the ONLY import path for cross-project vault writes (M-038)
_SHARED = r'C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils'
if _SHARED not in sys.path:
    sys.path.insert(0, _SHARED)

from vault_interface import write_to_vault  # noqa: E402


def parse_report_and_write(symbol: str, reports_dir: Path) -> bool:
    """Find latest report for symbol, extract data, write to Obsidian.

    Args:
        symbol:      Uppercase ticker string.
        reports_dir: Directory containing report_SYMBOL_*.txt files.

    Returns:
        True if note was written, False on skip or error.
    """

    # Find latest report for this symbol
    reports = sorted(reports_dir.glob(f"report_{symbol}_*_*.txt"), reverse=True)
    if not reports:
        print(f"[SKIP] {symbol}: no report found in {reports_dir}")
        return False

    report_file = reports[0]
    print(f"[PARSE] {symbol}: {report_file.name}")

    try:
        content = report_file.read_text()

        # Parse signal and horizon
        signal_match = re.search(r'Signal:\s+(\w+) at horizon (\d+)', content)
        if not signal_match:
            print(f"[FAIL] {symbol}: could not parse signal")
            return False

        signal_class = signal_match.group(1)
        horizon = int(signal_match.group(2))

        # Parse anchor date
        anchor_match = re.search(r'Anchor date:\s+(\d{4}-\d{2}-\d{2})', content)
        anchor_date = (
            anchor_match.group(1) if anchor_match
            else datetime.now().strftime("%Y-%m-%d")
        )

        # Build note body header
        body_lines = [f"# {symbol} - {signal_class} (h={horizon})", "", "## Per-Horizon Stats", ""]

        # Parse per-horizon stats table
        # Report columns: h  n  win_rate  mean_ret  std_ret  z_score  class
        # win_rate is a decimal fraction (0.800 = 80%) -- no /100 needed.
        # mean_ret is percentage points (+4.81 = 4.81%) -- strip leading +, no /100.
        stats_pattern = (
            r'^\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([+\-][\d.]+)'
            r'\s+([+\-]?[\d.]+)\s+([+\-]?[\d.]+)\s+(\w+)$'
        )
        h_win_rate = None
        h_mean_ret = None
        z_score = None

        for line in content.split('\n'):
            match = re.match(stats_pattern, line)
            if match:
                h_val = int(match.group(1))
                wr = float(match.group(3))       # already decimal: 0.800 = 80%
                mr = match.group(4)              # e.g. "+4.81"
                z = match.group(6)

                body_lines.append(f"**h={h_val}** | WR={wr * 100:.1f}% | MR={mr} | Z={z}")

                if h_val == horizon:
                    h_win_rate = wr                      # v1.1 fix: was wr / 100
                    h_mean_ret = float(mr.lstrip('+'))   # v1.1 fix: was float(mr.rstrip('%')) / 100
                    z_score = float(z)

        # Check for volatility divergence flag
        if 'VOLATILITY DIVERGENCE: MILD' in content or 'VOLATILITY DIVERGENCE: STRONG' in content:
            vol_match = re.search(r'VOLATILITY DIVERGENCE: (\w+)', content)
            if vol_match:
                severity = vol_match.group(1)
                body_lines.extend(["", "## Volatility Divergence", f"Severity: {severity}"])

        # Extract narrative section
        narrative_match = re.search(
            r'NARRATIVE\s*-+\s*(.*?)(?=={10,}|$)', content, re.DOTALL
        )
        if narrative_match:
            narrative_text = narrative_match.group(1).strip()
            body_lines.extend(["", "## Narrative", "", narrative_text])

        body = "\n".join(body_lines)

        # Build data payload for Hub interface.
        # NOTE: 'date' and 'anchor_date' are intentionally omitted -- P300Record v2.0
        # types both as Optional[datetime.date]; passing a string raises a Pydantic
        # coercion error. 'date' is deprecated in Note Standard v2.0. signal_date
        # carries the date semantics. anchor_date is informational only and is
        # captured in the body text above.
        trade_data = {
            "signal_date": anchor_date,                        # required by Note Standard v2.0
            "written_by": "P_300/daily_evaluate_pipeline",    # required by Note Standard v2.0
            "ticker": symbol,
            "signal": signal_class,
            "signal_horizon": horizon,
            "z_score": z_score,
            "vol_flag": "NONE",
        }

        if h_win_rate is not None:
            trade_data["h5_win_rate"] = h_win_rate if horizon == 5 else None
        if h_mean_ret is not None:
            trade_data["h5_mean_ret"] = h_mean_ret if horizon == 5 else None

        # Remove None values before passing to vault interface
        trade_data = {k: v for k, v in trade_data.items() if v is not None}

        # Write via Hub interface -- overwrite=True so re-runs update the existing note
        write_to_vault(
            schema_name="P300",
            data=trade_data,
            body=body,
            overwrite=True,
        )

        print(f"[OK] {symbol} written to vault")
        return True

    except Exception as e:
        print(f"[ERROR] {symbol}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python write_signal_to_obsidian.py SYMBOL")
        sys.exit(1)

    symbol = sys.argv[1]
    proj_root = Path(__file__).parent.parent
    reports_dir = proj_root / "outputs" / "reports"

    print(f"\n{'=' * 60}")
    print(f"OBSIDIAN SIGNAL WRITER")
    print(f"{'=' * 60}\n")

    ok = parse_report_and_write(symbol, reports_dir)
    sys.exit(0 if ok else 1)
