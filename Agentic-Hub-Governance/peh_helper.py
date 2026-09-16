"""
Agentic-Hub-Governance\peh_helper.py
PEH maintenance utility -- timestamped handoff filenames, pending-handoff
check, and retention archival. NOT imported by run_this_*.py scripts --
those stay self-contained and write their own .done marker inline.
Owner: P_000. Ref: WO-P000-E12.001, WO-P000-E11.001.

CHANGELOG:
  2026-09-10  Fixed .done vs .py.done naming drift (found during
              WO-P000-E23.001/E24.001 verify\ cleanup): two real completed
              handoffs (run_this_P118_20260903_145855, run_this_P300_
              20260904_095904) had their marker written as <stem>.done
              instead of the canonical <stem>.py.done, which both
              check_pending_handoffs() and archive_old_handoffs() required
              exactly -- both false-flagged as pending/never archived.
              check_pending_handoffs and archive_old_handoffs now accept
              either naming via _find_done_marker(); archive_old_handoffs
              iterates scripts (not just canonically-named .py.done files)
              so legacy-named sets are found too.
"""

import glob
import os
import shutil
from datetime import datetime, timedelta

VERIFY_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify"
ARCHIVE_DIR = os.path.join(VERIFY_DIR, "_archive")
RETENTION_DAYS = 14


def generate_handoff_filenames(project, verify_dir=VERIFY_DIR):
    """Return (script_path, context_path) for a new timestamped handoff.
    Filenames: run_this_<project>_<YYYYMMDD_HHMMSS>.py / _context.txt
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"run_this_{project}_{ts}"
    script_path = os.path.join(verify_dir, f"{stem}.py")
    context_path = os.path.join(verify_dir, f"{stem}_context.txt")
    return script_path, context_path


def _find_done_marker(script_path):
    """Return the actual .done marker path for a script, or None.

    Checks the canonical <script>.py.done first, then the legacy
    <script-without-.py>.done naming (drift discovered 2026-09-10).
    New scripts should always write the canonical form -- this is a
    read-side tolerance, not a license to keep writing the legacy form.
    """
    canonical = script_path + ".done"
    if os.path.exists(canonical):
        return canonical
    if script_path.endswith(".py"):
        legacy = script_path[:-3] + ".done"
        if os.path.exists(legacy):
            return legacy
    return None


def check_pending_handoffs(verify_dir=VERIFY_DIR):
    """Return run_this_*.py files with no matching .done sibling
    (either naming variant -- see _find_done_marker)."""
    pending = []
    for script_path in glob.glob(os.path.join(verify_dir, "run_this_*.py")):
        if _find_done_marker(script_path) is None:
            pending.append(script_path)
    return pending


def archive_old_handoffs(verify_dir=VERIFY_DIR, archive_dir=ARCHIVE_DIR,
                          retention_days=RETENTION_DAYS):
    """Move completed handoff sets (script + context + .done, either
    naming variant) whose .done file is older than retention_days into
    archive_dir. Incomplete handoffs (no .done) are never touched here.

    Iterates *.py scripts rather than *.py.done markers so legacy-named
    (<stem>.done) completed sets are found too, not just canonical ones.
    """
    os.makedirs(archive_dir, exist_ok=True)
    cutoff = datetime.now() - timedelta(days=retention_days)
    moved = []
    for script_path in glob.glob(os.path.join(verify_dir, "run_this_*.py")):
        done_path = _find_done_marker(script_path)
        if done_path is None:
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(done_path))
        if mtime < cutoff:
            _move_handoff_set(script_path, done_path, archive_dir)
            moved.append(script_path)
    return moved


def _move_handoff_set(script_path, done_path, archive_dir):
    """Move a script, its context file, and its .done marker together."""
    context_path = script_path.replace(".py", "_context.txt")
    for path in (script_path, context_path, done_path):
        if os.path.exists(path):
            shutil.move(path, os.path.join(archive_dir, os.path.basename(path)))


def done_marker_format():
    """Reference for the inline .done writer in generated run_this scripts.
    Three lines, written next to the script as <script>.py.done:
        timestamp: YYYY-MM-DD HH:MM:SS
        status: PASS|FAIL
        exit_code: <int>
    """
    return "timestamp: ...\nstatus: PASS|FAIL\nexit_code: <int>\n"


def main():
    """Standalone entry point: report pending handoffs, then archive old ones."""
    pending = check_pending_handoffs()
    if pending:
        print(f"UNCONSUMED HANDOFFS ({len(pending)}):")
        for p in pending:
            print(f"  {p}")
    else:
        print("No unconsumed handoffs.")

    moved = archive_old_handoffs()
    if moved:
        print(f"Archived {len(moved)} completed handoff(s) older than {RETENTION_DAYS} days.")


if __name__ == "__main__":
    main()
