"""
run_this_P300_20260831_081556.py
P_300 -- lessons.md archive pass (light, 8 entries) + M-111 duplicate-ID
rename to M-118. Approved by Tony 2026-08-31 (same session that found
the M-111 collision and the CLAUDE.md z-gate doc drift).

Moves M-042..M-051 (8 contiguous Section-1 entries, oldest-first,
2026-06-03 through 2026-06-12; cross-checked against SKILL/SIP/CLAUDE.md
-- none referenced) from tasks/lessons.md to tasks/lessons_archive.md
verbatim. Renames the OAuth-token M-111 (2026-08-19) to M-118, resolving
a duplicate-ID collision with the WO-status-header M-111 (~2026-08-12,
stays M-111). Fixes M-113's cross-reference to the renamed lesson; M-112's
reference to the OTHER M-111 is a different lesson and is deliberately
left untouched (asserted, not assumed). Backs up lessons.md first.
Verifies byte conservation and CR-byte count (M-117 guard) before PASS.
"""
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
LESSONS = PROJECT / "tasks" / "lessons.md"
ARCHIVE = PROJECT / "tasks" / "lessons_archive.md"
BACKUP_DIR = PROJECT / "tasks" / "_backup_20260831_archive_roll"

START_MARKER = "### M-042 -- Non-blocking hooks can hide silent failures; add explicit success logging"
END_MARKER = "## Section 2 -- Operational Lessons Specific to P_300 (Not Yet in EC Log)"

OLD_M111_HEADER = ('## M-111 -- M-097\'s "persists indefinitely" theory was wrong; '
                    'headless Claude Code OAuth tokens do not reliably refresh')
NEW_M118_HEADER = ('## M-118 -- M-097\'s "persists indefinitely" theory was wrong; '
                    'headless Claude Code OAuth tokens do not reliably refresh')

OLD_M113_REF = ('M-111 (headless auth reliability, same "one-off is fine, '
                 'pattern needs investigation" threshold)')
NEW_M113_REF = ('M-118 (headless auth reliability, same "one-off is fine, '
                 'pattern needs investigation" threshold)')

SURVIVING_M111 = "### M-111 -- A WO's Status header"
M112_UNTOUCHED_REF = "M-111 (header/body drift within one WO)"

EXPECTED_ARCHIVED_IDS = ['M-042', 'M-043', 'M-044', 'M-045', 'M-046', 'M-047', 'M-048', 'M-051']


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def main():
    if not LESSONS.exists():
        fail(f"lessons.md not found at {LESSONS}")

    orig_bytes = LESSONS.read_bytes()
    orig_cr, orig_lf, orig_size = orig_bytes.count(b'\r'), orig_bytes.count(b'\n'), len(orig_bytes)

    # newline='' -- raw passthrough, no universal-newline translation on
    # read OR write. This is the specific guard against M-117 (windows-mcp:
    # FileSystem mode=write silently normalizing LF->CRLF on a full rewrite).
    # p140 is 3.12; Path.read_text() gained newline= in 3.13. Use open()
    # so the M-117 raw-passthrough guard still applies.
    with LESSONS.open('r', encoding='utf-8', newline='') as f:
        text = f.read()

    start_idx = text.find(START_MARKER)
    end_idx = text.find(END_MARKER)
    if start_idx == -1:
        fail("START_MARKER (M-042 header) not found -- file structure changed since this script was written")
    if end_idx == -1:
        fail("END_MARKER (Section 2 header) not found")
    if end_idx <= start_idx:
        fail("END_MARKER precedes START_MARKER")

    archived_block = text[start_idx:end_idx]

    found_ids = [eid for eid in EXPECTED_ARCHIVED_IDS if f'### {eid} --' in archived_block]
    if len(found_ids) != 8:
        fail(f"expected 8 target IDs in archived span, found {len(found_ids)}: {found_ids}")
    all_headers_in_block = set(re.findall(r'### (M-\d+)', archived_block))
    if all_headers_in_block != set(EXPECTED_ARCHIVED_IDS):
        fail(f"unexpected headers inside archived span: {all_headers_in_block - set(EXPECTED_ARCHIVED_IDS)}")

    new_text = text[:start_idx] + text[end_idx:]

    if new_text.count(OLD_M111_HEADER) != 1:
        fail(f"expected exactly 1 occurrence of OLD_M111_HEADER, found {new_text.count(OLD_M111_HEADER)}")
    new_text = new_text.replace(OLD_M111_HEADER, NEW_M118_HEADER)

    if new_text.count(OLD_M113_REF) != 1:
        fail(f"expected exactly 1 occurrence of OLD_M113_REF, found {new_text.count(OLD_M113_REF)}")
    new_text = new_text.replace(OLD_M113_REF, NEW_M113_REF)

    if new_text.count(SURVIVING_M111) != 1:
        fail("surviving M-111 (WO status header) not found exactly once post-edit")
    if M112_UNTOUCHED_REF not in new_text:
        fail("M-112's correct M-111 cross-reference appears altered -- should be untouched")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LESSONS, BACKUP_DIR / "lessons.md")

    batch_note = (
        f"\n\n---\n\n## Archive batch -- {datetime.now().strftime('%Y-%m-%d')} "
        f"(4th archive roll, light pass)\n\n"
        f"8 Section-1 entries moved verbatim from tasks/lessons.md, oldest-first, "
        f"2026-06-03 through 2026-06-12, none referenced in SKILL/SIP/CLAUDE.md. "
        f"Script: {Path(__file__).name}\n\n"
    )
    with ARCHIVE.open('a', encoding='utf-8', newline='') as f:
        f.write(batch_note)
        f.write(archived_block)

    with LESSONS.open('w', encoding='utf-8', newline='') as f:
        f.write(new_text)

    new_bytes = LESSONS.read_bytes()
    new_cr, new_lf = new_bytes.count(b'\r'), new_bytes.count(b'\n')
    cr_removed = archived_block.count('\r')
    lf_removed = archived_block.count('\n')
    expected_new_cr = orig_cr - cr_removed
    expected_new_lf = orig_lf - lf_removed
    removed_len = len(archived_block.encode('utf-8'))
    actual_delta = orig_size - len(new_bytes)
    new_entry_count = len(re.findall(r'^#{2,3} (M|O|S)-\d+', new_text, re.MULTILINE))

    print(f"Original lessons.md: {orig_size} bytes, CR={orig_cr}, LF={orig_lf}")
    print(f"New lessons.md:      {len(new_bytes)} bytes, CR={new_cr}, LF={new_lf}")
    print(f"Archived span:       {removed_len} bytes, ids moved: {found_ids}")
    print(f"Byte delta (expect ~{removed_len}): {actual_delta}")
    print(f"M/O/S entry count: 43 -> {new_entry_count}")
    print(f"Rename applied: M-111 (OAuth, 08-19) -> M-118; M-113 ref updated to match")
    print(f"Surviving M-111 (WO status header) intact; M-112's reference to it untouched")
    print(f"Backup: {BACKUP_DIR / 'lessons.md'}")

    if abs(actual_delta - removed_len) > 2:
        fail(f"byte delta {actual_delta} does not match archived span {removed_len}")
    if new_cr != expected_new_cr:
        fail(f"CR count mismatch: expected {expected_new_cr} (orig {orig_cr} - removed {cr_removed}), got {new_cr} -- possible line-ending mutation (M-117)")
    if new_lf != expected_new_lf:
        fail(f"LF count mismatch: expected {expected_new_lf}, got {new_lf}")

    done_path = Path(__file__).with_suffix('.done')
    done_path.write_text(f"PASS\n0\n{datetime.now().isoformat()}\n", encoding='utf-8')

    print("PASS")


if __name__ == "__main__":
    main()
