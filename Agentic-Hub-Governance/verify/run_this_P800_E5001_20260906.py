"""
run_this_P800_E5001_20260906.py

WO-P800-E5.001 -- KnowledgeBase Folder Split (Newsletter vs Research)

WHAT THIS DOES
--------------
1. Backs up config.py and filename_builder.py (obsidian_writers) with a
   .backup_2026-09-06 suffix -- originals are never overwritten without
   a copy sitting next to them first.
2. Adds KB_ORIGIN_SUBFOLDER_MAP to config.py: a KB-schema write whose
   origin is "Email" routes to KnowledgeBase\\Newsletters\\ instead of
   the KnowledgeBase root. Every other origin (Web Clipper, PDF, AI
   Summary, Manual, or unset) is unaffected.
3. Updates filename_builder.py's build_filepath() to consult that map
   for the KB schema only. No other schema's routing changes.
4. Creates trading_journal\\KnowledgeBase\\Newsletters\\ if it isn't
   there yet.
5. Runs a LIVE smoke test: writes one real KB note with origin="Email"
   and one with origin="Web Clipper" through the actual write_to_vault()
   path, confirms each landed in the folder it should have, then deletes
   both test notes so nothing fake is left in your vault.
6. Prints a clear PASS/FAIL summary.

NOT TOUCHED (confirmed unnecessary -- see WO-P800-E5.001 for why):
  - write_handler.py -- only calls build_filepath(); routing logic lives
    entirely in filename_builder.py.
  - vault_schemas.py -- KBRecord already has an `origin` field.
  - KB_Articles.base -- Obsidian's file.inFolder("KnowledgeBase") filter
    matches nested subfolders, so Newsletters\\ shows up automatically.

HOW TO RUN
----------
Open a normal terminal (not through Claude/Windows-MCP) and run:

    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe C:\\Users\\Trader\\AI-Agent-Learning-Hub\\Agentic-Hub-Governance\\verify\\run_this_P800_E5001_20260906.py

Read the PASS/FAIL block at the end. If it says FAIL, nothing further
happens automatically -- paste the output back and we'll look at it
together. The .backup_2026-09-06 files stay in place either way, so a
manual revert is always available (just copy them back over the originals).
"""

import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
OW_ROOT = HUB_ROOT / "obsidian_writers"
CONFIG_PATH = OW_ROOT / "config.py"
FILENAME_BUILDER_PATH = OW_ROOT / "domain" / "filename_builder.py"
NEWSLETTERS_DIR = HUB_ROOT / "trading_journal" / "KnowledgeBase" / "Newsletters"
DATE_STAMP = "2026-09-06"
MARKER = "KB_ORIGIN_SUBFOLDER_MAP"


def backup(path: Path) -> None:
    backup_path = path.with_name(f"{path.name}.backup_{DATE_STAMP}")
    if backup_path.exists():
        print(f"  SKIP backup (already exists): {backup_path}")
    else:
        shutil.copy2(path, backup_path)
        print(f"  Backed up: {backup_path}")


def patch_config(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("  SKIP config.py -- KB_ORIGIN_SUBFOLDER_MAP already present.")
        return

    anchor = '    "KB":       "KnowledgeBase",\n}'
    if anchor not in text:
        print("  FAIL: expected VAULT_FOLDER_MAP anchor not found in config.py.")
        sys.exit(1)

    addition = (
        '    "KB":       "KnowledgeBase",\n}\n\n'
        "# -- KB SCHEMA ORIGIN SUBFOLDER MAP -----------------------------------------\n"
        "# WO-P800-E5.001 (2026-09-06). A KB write whose origin matches a key here\n"
        "# routes to VAULT_ROOT / <value> instead of VAULT_FOLDER_MAP[\"KB\"] --\n"
        "# keeps P_805 newsletter-derived KB notes separate from manually-clipped\n"
        "# research in the same KnowledgeBase tree. Any origin not listed here\n"
        "# (Web Clipper, PDF, AI Summary, Manual, or unset) uses the KB root,\n"
        "# unchanged. Consulted only by filename_builder.build_filepath() for\n"
        "# the KB schema -- no other schema is affected.\n"
        "KB_ORIGIN_SUBFOLDER_MAP: dict[str, str] = {\n"
        '    "Email": "KnowledgeBase/Newsletters",\n'
        "}"
    )
    path.write_text(text.replace(anchor, addition, 1), encoding="utf-8")
    print("  Patched config.py -- added KB_ORIGIN_SUBFOLDER_MAP.")


def patch_filename_builder(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("  SKIP filename_builder.py -- origin-aware routing already present.")
        return

    old_import = (
        "from obsidian_writers.config import (\n"
        "    JSON_FILENAME_SUFFIX,\n"
        "    OUTPUT_FORMAT,\n"
        "    VAULT_FOLDER_MAP,\n"
        "    VAULT_ROOT,\n"
        ")"
    )
    new_import = (
        "from obsidian_writers.config import (\n"
        "    JSON_FILENAME_SUFFIX,\n"
        "    KB_ORIGIN_SUBFOLDER_MAP,\n"
        "    OUTPUT_FORMAT,\n"
        "    VAULT_FOLDER_MAP,\n"
        "    VAULT_ROOT,\n"
        ")"
    )
    if old_import not in text:
        print("  FAIL: expected import block not found in filename_builder.py.")
        sys.exit(1)
    text = text.replace(old_import, new_import, 1)

    old_folder_line = "    folder = VAULT_ROOT / VAULT_FOLDER_MAP[schema_name]\n"
    new_folder_block = (
        '    if schema_name == "KB":\n'
        "        # WO-P800-E5.001: route by origin when a subfolder is mapped,\n"
        "        # otherwise fall back to the ordinary KB root folder.\n"
        '        override = KB_ORIGIN_SUBFOLDER_MAP.get(data.get("origin"))\n'
        "        folder = VAULT_ROOT / (override or VAULT_FOLDER_MAP[schema_name])\n"
        "    else:\n"
        "        folder = VAULT_ROOT / VAULT_FOLDER_MAP[schema_name]\n"
    )
    if old_folder_line not in text:
        print("  FAIL: expected folder-assignment line not found in filename_builder.py.")
        sys.exit(1)
    text = text.replace(old_folder_line, new_folder_block, 1)

    path.write_text(text, encoding="utf-8")
    print("  Patched filename_builder.py -- origin-aware KB routing added.")


def _check_note(label: str, path: Path, should_be_in_newsletters: bool) -> bool:
    in_newsletters = "Newsletters" in path.parts
    ok = path.exists() and (in_newsletters == should_be_in_newsletters)
    print(f"  {label} -> {path}")
    print(f"    exists={path.exists()}  in Newsletters\\={in_newsletters}  expected_in_Newsletters={should_be_in_newsletters}")
    return ok


def run_smoke_test() -> bool:
    sys.path.insert(0, str(HUB_ROOT))
    from shared_resources.python_utils.vault_interface import write_to_vault
    from obsidian_writers.domain.filename_builder import build_filepath

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%S")
    base = {
        "signal_date": "2026-09-06",
        "kb_type": "Article",
        "written_by": "WO-P800-E5.001/smoke_test",
    }
    email_data = {**base, "title": f"WO-P800-E5001 smoke test email {stamp}", "origin": "Email"}
    clipper_data = {**base, "title": f"WO-P800-E5001 smoke test clipper {stamp}", "origin": "Web Clipper"}

    ok_email = write_to_vault("KB", dict(email_data))
    ok_clipper = write_to_vault("KB", dict(clipper_data))

    resolved = {**email_data, "run_date": now.strftime("%Y-%m-%d"), "run_ts": now.isoformat()}
    email_path = build_filepath("KB", resolved)
    resolved = {**clipper_data, "run_date": now.strftime("%Y-%m-%d"), "run_ts": now.isoformat()}
    clipper_path = build_filepath("KB", resolved)

    email_ok = ok_email and _check_note("Email-origin note   ", email_path, should_be_in_newsletters=True)
    clipper_ok = ok_clipper and _check_note("Web Clipper-origin note", clipper_path, should_be_in_newsletters=False)

    for p in (email_path, clipper_path):
        try:
            if p.exists():
                p.unlink()
                print(f"  Cleaned up test note: {p}")
        except OSError as e:
            print(f"  WARNING: could not delete test note {p}: {e}")

    return bool(email_ok and clipper_ok)


def main() -> None:
    print("=" * 70)
    print("WO-P800-E5.001 -- KnowledgeBase Folder Split")
    print("=" * 70)

    print("\n[1/4] Backing up files...")
    backup(CONFIG_PATH)
    backup(FILENAME_BUILDER_PATH)

    print("\n[2/4] Patching config.py...")
    patch_config(CONFIG_PATH)

    print("\n[3/4] Patching filename_builder.py...")
    patch_filename_builder(FILENAME_BUILDER_PATH)

    print("\n[4/4] Ensuring KnowledgeBase\\Newsletters\\ exists...")
    NEWSLETTERS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  Confirmed: {NEWSLETTERS_DIR}")

    print("\nRunning live smoke test (writes + deletes two real test KB notes)...")
    try:
        passed = run_smoke_test()
    except Exception:
        print("  FAIL -- smoke test raised an exception:")
        traceback.print_exc()
        passed = False

    print("\n" + "=" * 70)
    if passed:
        print("RESULT: PASS -- Email-origin KB writes route to Newsletters\\,")
        print("        all other origins route to KnowledgeBase\\ root, unaffected.")
    else:
        print("RESULT: FAIL -- see output above. Backups are in place regardless;")
        print("        paste this full output back for a look before retrying.")
    print("=" * 70)


if __name__ == "__main__":
    main()
