r"""One-off: pull one real message from an enabled P_805 sender out of the
Thunderbird mbox cache and save it as a standalone .eml in data\inbox\ for
the WO-P800-E5.001 criterion 4 --kb-mode test.

Not part of the permanent P_805 codebase - staging script only.
"""

import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

import config  # noqa: E402
from domain.sender_filter import extract_email_address  # noqa: E402
from infrastructure.mbox_reader import iter_mbox_messages  # noqa: E402
from infrastructure.sender_sheet import load_enabled_senders  # noqa: E402

enabled = load_enabled_senders()
print(f"Enabled senders loaded: {len(enabled)}")

inbox_dir = config.PROJECT_ROOT / "data" / "inbox"
inbox_dir.mkdir(parents=True, exist_ok=True)

found = False
for account, rel_path in config.MBOX_FILES.items():
    mbox_path = config.PROFILE_ROOT / rel_path
    if not mbox_path.exists():
        print(f"[{account}] mbox not found: {mbox_path}")
        continue

    print(f"[{account}] scanning {mbox_path}")
    checked = 0
    for msg in iter_mbox_messages(mbox_path):
        checked += 1
        addr = extract_email_address(msg.get("From"))
        if addr and addr in enabled:
            subject = msg.get("Subject", "no-subject")
            safe_addr = addr.replace("@", "_at_").replace(".", "_")
            out_path = inbox_dir / f"staged_{account}_{safe_addr}.eml"
            with open(out_path, "wb") as f:
                f.write(msg.as_bytes())
            print(f"MATCH after {checked} messages: {addr}")
            print(f"Subject: {subject}")
            print(f"Written: {out_path}")
            found = True
            break
    if found:
        break
    print(f"[{account}] no enabled-sender match in {checked} messages")

if not found:
    print("No enabled-sender message found in any account mbox.")
