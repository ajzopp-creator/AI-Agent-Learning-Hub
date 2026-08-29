"""
FILE: run_this_P300_20260829_104500.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Anthony Zoppi + Claude
LAYER: verify (PEH handoff, one-off maintenance, self-contained)
DESCRIPTION:
    WO-P000-E8.001 third archive pass for P_300 tasks/todo.md and
    tasks/lessons.md. Mechanical, reversible: backs up first, moves
    whole entries verbatim to the _archive files, checks byte
    conservation and entry counts, never deletes text.
"""
from __future__ import annotations

import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_300_Vantage_Point_Pattern_Recognition"
)
TASKS = PROJECT / "tasks"
TODO, TODO_ARC = TASKS / "todo.md", TASKS / "todo_archive.md"
LES, LES_ARC = TASKS / "lessons.md", TASKS / "lessons_archive.md"
BACKUP = TASKS / "_backup_20260829_archive_roll"
REF_DOCS = [
    PROJECT / ".claude" / "skills" / "p300-project-context" / "SKILL.md",
    PROJECT / "docs" / "P_300_System_Initialization_Prompt_v3_1.md",
    PROJECT / "CLAUDE.md",
]
TOP_KEEP_FROM = date(2026, 8, 21)
BOTTOM_KEEP_FROM = date(2026, 8, 23)
LESSONS_CAP = 40
TODO_LOG_CAP = 500
SCRIPT_TAG = "verify\\run_this_P300_20260829_104500.py"

_TODO_MARK = re.compile(r"^(\*\*>>> |## )(\d{4}-\d{2}-\d{2})")
_HEAD = re.compile(r"^(#{2,3}) ")
_ENTRY = re.compile(r"^#{2,3} ((?:M|O|S)-(\d+))")

added_bytes = 0
NL = "\n"


def _read(p: Path) -> list[str]:
    with p.open("r", encoding="utf-8", newline="") as f:
        return f.read().splitlines(keepends=True)


def _write(p: Path, lines: list[str]) -> None:
    with p.open("w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))


def _nb(s: str) -> int:
    return len(s.encode("utf-8"))


def _add(s: str) -> str:
    """Normalize inserted text to the target file's line ending, count it."""
    global added_bytes
    s = s.replace("\r\n", NL)
    added_bytes += _nb(s)
    return s


def _set_nl(lines: list[str]) -> None:
    global NL
    NL = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"


def partition_dated(lines: list[str], keep_from: date) -> tuple[list[str], list[str]]:
    """Split a block of dated entries into (keep, archive). Lines before
    the first marker are always kept (preamble)."""
    keep: list[str] = []
    arc: list[str] = []
    cur: list[str] = []
    cur_old = False
    started = False

    def flush() -> None:
        (arc if cur_old else keep).extend(cur)

    for ln in lines:
        m = _TODO_MARK.match(ln)
        if m:
            if started:
                flush()
            started = True
            cur = [ln]
            d = datetime.strptime(m.group(2), "%Y-%m-%d").date()
            cur_old = d < keep_from
        elif started:
            cur.append(ln)
        else:
            keep.append(ln)
    if started:
        flush()
    return keep, arc


def roll_todo() -> tuple[int, int, int]:
    lines = _read(TODO)
    _set_nl(lines)
    i_ret = next(i for i, l in enumerate(lines)
                 if l.startswith("## Working-State Doc Retention"))
    i_end = next(i for i, l in enumerate(lines)
                 if l.startswith("**End of P_300 Task Queue**"))
    top, mid, bottom = lines[:i_ret], lines[i_ret:i_end + 1], lines[i_end + 1:]
    top_keep, top_arc = partition_dated(top, TOP_KEEP_FROM)
    bot_keep, bot_arc = partition_dated(bottom, BOTTOM_KEEP_FROM)

    note_i = next(i for i, l in enumerate(mid)
                  if l.startswith("See tasks/todo_archive.md and WO-P000-E8.001"))
    note = _add("Third pass: 2026-08-29, top-block entries dated before\r\n"
                "2026-08-21 and appended (out-of-order) entries dated before\r\n"
                f"2026-08-23 archived, mechanically, via {SCRIPT_TAG}.\r\n")
    mid = mid[:note_i] + [note] + mid[note_i:]

    arc = _read(TODO_ARC)
    sep = next(i for i, l in enumerate(arc) if l.strip() == "---")
    head = _add("\r\n## Third archive pass -- 2026-08-29\r\n\r\n"
                "Top-block entries (newest-first, as they stood live), then "
                "out-of-order appended entries in their original order. "
                f"Script: {SCRIPT_TAG}.\r\n\r\n")
    tail = _add("\r\n---\r\n")
    gap = _add("\r\n")
    arc = arc[:sep + 1] + [head] + top_arc + [gap] + bot_arc + [tail] + arc[sep + 1:]

    _write(TODO, top_keep + mid + bot_keep)
    _write(TODO_ARC, arc)
    n_top = sum(1 for l in top_arc if _TODO_MARK.match(l))
    n_bot = sum(1 for l in bot_arc if _TODO_MARK.match(l))
    return n_top, n_bot, len(top_keep) + len(bot_keep)


def _entry_spans(lines: list[str]) -> list[tuple[str, int, int, int]]:
    """(id, number, start, end) for every M/O/S entry; end exclusive."""
    heads = [i for i, l in enumerate(lines) if _HEAD.match(l)]
    spans = []
    for k, i in enumerate(heads):
        m = _ENTRY.match(lines[i])
        if not m:
            continue
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        spans.append((m.group(1), int(m.group(2)), i, end))
    return spans


def _referenced_ids() -> str:
    text = ""
    for p in REF_DOCS:
        if p.exists():
            text += p.read_text(encoding="utf-8", errors="replace")
        else:
            print(f"  note: ref doc missing, skipped: {p}")
    return text


def choose_archive(lines: list[str]) -> tuple[list[tuple[str, int, int, int]], list[str]]:
    spans = _entry_spans(lines)
    need = len(spans) - LESSONS_CAP
    if need <= 0:
        return [], []
    s1 = next(i for i, l in enumerate(lines) if l.startswith("## Section 1 "))
    s2 = next(i for i, l in enumerate(lines) if l.startswith("## Section 2 "))
    refs = _referenced_ids()
    cands = sorted((s for s in spans if s1 < s[2] < s2 and s[0].startswith("M-")),
                   key=lambda s: s[1])
    chosen, skipped = [], []
    for s in cands:
        if len(chosen) >= need:
            break
        if re.search(rf"\b{re.escape(s[0])}\b", refs):
            skipped.append(s[0])
            continue
        chosen.append(s)
    return chosen, skipped


def roll_lessons() -> tuple[int, int, list[str], list[str]]:
    lines = _read(LES)
    _set_nl(lines)
    before = len(_entry_spans(lines))
    chosen, skipped = choose_archive(lines)
    drop = set()
    archived_text: list[str] = []
    for _id, _n, a, b in chosen:
        archived_text.extend(lines[a:b])
        drop.update(range(a, b))

    old_lu = lines[4]
    if not old_lu.startswith("**Last Updated:**"):
        raise RuntimeError("lessons.md line 5 is not the Last Updated line")
    new_lu = _add("**Last Updated:** 2026-08-29 (M-114). Full per-session update "
                  "history moved to tasks/lessons_archive.md, third pass.\r\n")
    live = [new_lu if i == 4 else l for i, l in enumerate(lines) if i not in drop]

    ret_i = next(i for i, l in enumerate(live)
                 if l.startswith("## Working-State Doc Retention"))
    sep_i = next(i for i in range(ret_i + 1, len(live)) if live[i].strip() == "---")
    note = _add(f"Third pass: 2026-08-29 -- {len(chosen)} Section 1 entries archived "
                "oldest-first, skipping IDs still referenced in SKILL/SIP/CLAUDE.md "
                f"({', '.join(skipped) or 'none'}); Last-Updated history line moved "
                f"to the archive. Script: {SCRIPT_TAG}.\r\n\r\n")
    live = live[:sep_i] + [note] + live[sep_i:]

    arc = _read(LES_ARC)
    head = _add("\r\n\r\n---\r\n\r\n## Third archive pass -- 2026-08-29 "
                "(age-based: oldest Section 1 entries not referenced in "
                "SKILL/SIP/CLAUDE.md)\r\n\r\n"
                "**Archived Last-Updated history line from lessons.md:**\r\n\r\n")
    mid = _add("\r\n")
    arc = arc + [head, old_lu, mid] + archived_text
    _write(LES, live)
    _write(LES_ARC, arc)
    return before, len(_entry_spans(live)), [c[0] for c in chosen], skipped


def _done(status: str, code: int) -> None:
    Path(__file__).with_suffix(".py.done").write_text(
        f"timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"status: {status}\nexit_code: {code}\n", encoding="utf-8")


def main() -> int:
    BACKUP.mkdir(exist_ok=True)
    for p in (TODO, TODO_ARC, LES, LES_ARC):
        shutil.copy2(p, BACKUP / p.name)
    print(f"backup: {BACKUP}")
    bytes_before = sum(p.stat().st_size for p in (TODO, TODO_ARC, LES, LES_ARC))

    n_top, n_bot, log_lines = roll_todo()
    print(f"todo.md: archived {n_top} top-block + {n_bot} appended entries; "
          f"dated-log portion now {log_lines} lines (cap {TODO_LOG_CAP})")
    before, after, chosen, skipped = roll_lessons()
    print(f"lessons.md: {before} -> {after} entries (cap {LESSONS_CAP})")
    print(f"  archived: {', '.join(chosen)}")
    print(f"  kept (referenced): {', '.join(skipped) or 'none'}")

    bytes_after = sum(p.stat().st_size for p in (TODO, TODO_ARC, LES, LES_ARC))
    delta = bytes_after - bytes_before
    print(f"bytes: before={bytes_before} after={bytes_after} "
          f"delta={delta} expected_added={added_bytes}")
    for p in (TODO, LES):
        print(f"  {p.name}: {p.stat().st_size} bytes, {len(_read(p))} lines")
    ok = (delta == added_bytes and log_lines <= TODO_LOG_CAP
          and after <= LESSONS_CAP)
    if not ok:
        print("FAIL: invariant broken -- restore from backup, do not hand-edit")
        _done("FAIL", 1)
        return 1
    print("PASS")
    _done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
