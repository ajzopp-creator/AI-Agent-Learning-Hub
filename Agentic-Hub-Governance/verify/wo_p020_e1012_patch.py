"""WO-P020-E1.012 -- correct the Session INIT command block.

Dry-run by default. Pass --commit to write.
Patches: system doc Section 9.6, system doc Section 8, SIP Step 2, SIP changelog.
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
            r"\P_020_AJZStrategies_PerformanceAnalysisSystem")
DOC = ROOT / "docs" / "P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md"
SIP = ROOT / "SESSION_INITIALIZATION_PROMPT_v2_9.md"
STAMP = "2026-08-04"

BT = "`" * 3

OLD_96 = (
    "**Rule:** NEVER `Start-Process -NoNewWindow` (blocks MCP ~4 min). "
    "ALWAYS `Start-Job + cmd /c`.\n"
)

NEW_96 = (
    "**Rule:** NEVER `Start-Process -NoNewWindow` (blocks MCP ~4 min). "
    "NEVER `Start-Job` -- each Windows-MCP call is an isolated process, the job is "
    "torn down when the call returns and the output file is never written "
    "(WO-P020-E1.012). ALWAYS `Start-Process -WindowStyle Hidden` with redirected "
    "stdout/stderr, read back in a SEPARATE call.\n"
)

OLD_BLOCK_START = BT + "powershell\n$job = Start-Job"
NEW_BLOCK = (
    BT + "powershell\n"
    '$ts  = Get-Date -Format "HHmmss"\n'
    '$out = "C:\\Temp\\init_$ts.txt"\n'
    '$err = "C:\\Temp\\initerr_$ts.txt"\n'
    'Start-Process -FilePath "C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe" `\n'
    "  -ArgumentList '\"C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects"
    "\\P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\P_020_INIT.py\"' `\n"
    "  -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err\n"
    '"OUT=$out"; "ERR=$err"\n'
    "# Separate tool call -- Get-Content $out -Raw    (NO Start-Sleep: it stalls the relay)\n"
    + BT + "\n"
)

ERR_ANCHOR = "*Errors are never deleted \u2014 only marked Resolved.*\n"
ERR_ENTRY = (
    "\n### Error: INIT Command Block Used Start-Job \u2014 Output File Never Written\n"
    "- **Date:** 2026-08-03 | **Severity:** Medium | **Status:** Resolved\n"
    "- **Wrong:** Section 9.6 mandated `Start-Job + cmd /c`. Each Windows-MCP "
    "PowerShell call is an isolated process; the job is killed when the call returns, "
    "before `cmd /c` flushes to disk. `C:\\Temp\\init_out.txt` was never created. "
    "Broken since 2026-06-18, hit every session INIT.\n"
    "- **Secondary:** `Start-Sleep` inside the read-back MCP call stalled the relay for "
    "the full 4-minute timeout. Never sleep inside an MCP call.\n"
    "- **Fix:** Section 9.6 rewritten to `Start-Process -WindowStyle Hidden` with "
    "redirected stdout/stderr to uniquely-timestamped files, read back in a separate "
    "call. `-WindowStyle Hidden` is NOT the banned `-NoNewWindow`. WO-P020-E1.012.\n"
    "- **Verify:** Cold session, run Section 9.6 block, second call returns the INIT "
    "output block with no timeout.\n"
)

OLD_SIP = (
    "Use the `Start-Job + cmd /c` command block in "
    "`docs\\P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md` Section 9.6. "
    "NEVER use `Start-Process -NoNewWindow`."
)
NEW_SIP = (
    "Use the `Start-Process -WindowStyle Hidden` + redirect command block in "
    "`docs\\P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md` Section 9.6. "
    "NEVER use `Start-Process -NoNewWindow` or `Start-Job` (WO-P020-E1.012). "
    "Never put `Start-Sleep` in an MCP call."
)

CL_ANCHOR = "## Changelog\n"
CL_ENTRY = (
    "\n### v3.2 \u2014 2026-08-03\n"
    "- Step 2 INIT invocation corrected. `Start-Job` banned (does not survive an "
    "isolated MCP call); `Start-Process -WindowStyle Hidden` + redirect is the "
    "working pattern. WO-P020-E1.012.\n"
)


def patch(text, old, new, label, report):
    n = text.count(old)
    report.append(f"  {label}: {n} match(es)")
    if n != 1:
        report.append(f"  !! ABORT -- expected exactly 1 for {label}")
        return text, False
    return text.replace(old, new, 1), True


def replace_block(text, report):
    i = text.find(OLD_BLOCK_START)
    report.append(f"  9.6 code block: {'found' if i >= 0 else 'NOT FOUND'}")
    if i < 0:
        return text, False
    j = text.find(BT, text.find("\n", i))
    if j < 0:
        report.append("  !! ABORT -- unterminated fence")
        return text, False
    return text[:i] + NEW_BLOCK + text[j + 4:], True


def main():
    commit = "--commit" in sys.argv
    report = ["WO-P020-E1.012 patch  |  MODE: " + ("COMMIT" if commit else "DRY-RUN")]
    ok = True

    for path in (DOC, SIP):
        if not path.exists():
            report.append(f"MISSING: {path}")
            ok = False
    if not ok:
        print("\n".join(report))
        return 1

    doc = DOC.read_text(encoding="utf-8")
    report.append(f"\n{DOC.name}")
    doc, a = patch(doc, OLD_96, NEW_96, "9.6 rule line", report)
    doc, b = replace_block(doc, report)
    doc, c = patch(doc, ERR_ANCHOR, ERR_ANCHOR + ERR_ENTRY, "Section 8 entry", report)

    sip = SIP.read_text(encoding="utf-8")
    report.append(f"\n{SIP.name}")
    sip, d = patch(sip, OLD_SIP, NEW_SIP, "Step 2 pointer", report)
    sip, e = patch(sip, CL_ANCHOR, CL_ANCHOR + CL_ENTRY, "changelog v3.2", report)

    if not all([a, b, c, d, e]):
        report.append("\nRESULT: ABORTED -- nothing written.")
        print("\n".join(report))
        return 1

    if commit:
        for path, new_text in ((DOC, doc), (SIP, sip)):
            bak = path.with_name(f"{path.stem}_backup_{STAMP}{path.suffix}")
            bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            path.write_text(new_text, encoding="utf-8")
            report.append(f"  wrote {path.name}  (backup: {bak.name})")
        report.append("\nRESULT: COMMITTED")
    else:
        report.append("\nRESULT: DRY-RUN OK -- all 5 anchors matched. Re-run with --commit.")

    print("\n".join(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
