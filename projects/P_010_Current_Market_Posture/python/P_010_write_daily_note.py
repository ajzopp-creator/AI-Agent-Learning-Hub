"""
P_010 Daily Note Writer -- Orchestration (v2.1, WO-P010-E1.003 staleness check)
Loads risk config + snapshot, fetches live content, renders via template engine
(or hardcoded fallback), writes the Obsidian daily note. Never overwrites an
existing note. Logic moved to note_api_fetchers.py / note_content_builders.py /
note_template_engine.py -- this file is orchestration only.

WO-P010-E1.003: checks P_010_RiskConfig.json's internal "timestamp" against
today's date (staleness_check.is_morning_data_stale -- keys off timestamp,
NOT grid_date, since grid_date legitimately lags over weekends). If stale,
the note is written with a [STALE POSTURE -- MANUAL REVIEW] banner instead
of the normal Section 5 VP table, so a failed/carryover morning run never
gets written up as if it were fresh data.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from note_api_fetchers import fetch_scripture, fetch_quote, fetch_joke
from note_template_engine import find_latest_template, process_template, build_fallback_note
from staleness_check import is_morning_data_stale

# -- Paths ---------------------------------------------------------------------
VAULT_PATH   = Path(r"C:\Users\Trader\Documents\AJZStrategies_TradingJournal\Trading Journal")
NOTES_FOLDER = VAULT_PATH / "TradingJournal"
PROJECT_ROOT = Path(__file__).parent.parent
RISK_CONFIG  = PROJECT_ROOT / "P_010_RiskConfig.json"
SNAPSHOT     = PROJECT_ROOT / "grid_snapshot_latest.json"
SKIP_FLAG    = PROJECT_ROOT / "SKIP_TODAY.flag"
DATE_FORMAT  = "%m-%d-%Y"


def load_risk_config():
    if not RISK_CONFIG.exists():
        print(f"  WARNING: {RISK_CONFIG.name} not found -- posture fields will show N/A")
        return {}
    with open(RISK_CONFIG) as f:
        return json.load(f)


def load_snapshot():
    if not SNAPSHOT.exists():
        print(f"  WARNING: {SNAPSHOT.name} not found -- price table will show --")
        return {}
    with open(SNAPSHOT) as f:
        return json.load(f)


def build_stale_banner(cfg, now):
    """Used when today's posture data failed to refresh (timestamp isn't today)."""
    ts = cfg.get("timestamp", "unknown")
    return f"""> [!danger] STALE POSTURE -- MANUAL REVIEW
> P_010_RiskConfig.json's internal timestamp ({ts}) is not from today's run.
> The morning posture script may have failed or been skipped -- do NOT trust
> the risk_mode / avg_posture fields below for sizing decisions until this
> is manually confirmed against a fresh run.
>
> Check MORNING_RUN_FAILED.flag and today's P_010_Daily_*.log, then re-run
> P_010_daily_posture.bat manually once the underlying issue is fixed.

Last known values (STALE, for reference only):
- risk_mode: {cfg.get('risk_mode', 'N/A')}
- avg_posture: {cfg.get('avg_posture', 'N/A')}
- timestamp: {ts}
"""


def main():
    now = datetime.now()
    print("=" * 70)
    print("P_010 DAILY NOTE WRITER v2.1 -- Template-Driven")
    print("=" * 70)
    print(f"Time  : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Guards
    if SKIP_FLAG.exists():
        print("SKIP_TODAY.flag found -- skipping note creation"); return 0
    if now.weekday() >= 5:
        print(f"Today is {now.strftime('%A')} -- markets closed, skipping"); return 0

    # Load data
    cfg  = load_risk_config()
    snap = load_snapshot()
    print(f"  Risk Mode  : {cfg.get('risk_mode','N/A')}")
    print(f"  Avg Posture: {cfg.get('avg_posture','N/A')}")
    print(f"  VXX Signal : {cfg.get('vxx_signal','N/A')}")

    stale = is_morning_data_stale(cfg, now.date())
    if stale:
        print(f"  WARNING: posture data is STALE -- timestamp is not from today")
    print()

    # Fetch live content
    print("  Fetching scripture..."); scripture = fetch_scripture()
    print("  Fetching quote...");     quote     = fetch_quote()
    print("  Fetching humor...");     joke      = fetch_joke()
    print()

    # Find template
    template_path, version = find_latest_template()
    if template_path:
        print(f"  Template   : {template_path.name} (v{version})")
        template_text = template_path.read_text(encoding="utf-8")
        note = process_template(template_text, now, cfg, snap, scripture, quote, joke)
        source = f"template {template_path.name}"
    else:
        print("  WARNING: No P_010_TemplateSchema_v*.md found -- using hardcoded fallback")
        note = build_fallback_note(now, cfg, snap, scripture, quote, joke)
        source = "hardcoded fallback"

    # Staleness override: prepend the banner regardless of which path built the note.
    # Deliberately does NOT suppress the rest of the note (scripture/quote/joke/log
    # sections still have value) -- only the posture-trust framing changes.
    if stale:
        note = build_stale_banner(cfg, now) + "\n---\n\n" + note
        source += " [STALE POSTURE OVERRIDE]"

    # Write note
    NOTES_FOLDER.mkdir(parents=True, exist_ok=True)
    fn = now.strftime(DATE_FORMAT) + ".md"
    tf = NOTES_FOLDER / fn

    if tf.exists():
        print()
        print("=" * 70)
        print(f"  NOTE ALREADY EXISTS -- SKIPPING")
        print(f"  File   : {tf}")
        print(f"  Action : Note will NOT be overwritten")
        print(f"  To regenerate: delete {fn} from TradingJournal/ and re-run morning batch")
        print("=" * 70)
        return 0

    tf.write_text(note, encoding="utf-8")

    print()
    print("=" * 70)
    print("DAILY NOTE CREATED")
    print("=" * 70)
    print(f"  File   : {tf}")
    print(f"  Size   : {tf.stat().st_size} bytes")
    print(f"  Source : {source}")
    print(f"  Open Obsidian -- note ready in TradingJournal/")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
