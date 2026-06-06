import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from email import message_from_binary_file
from email.utils import parsedate_to_datetime

THUNDERBIRD_PROFILES = Path(r"C:\Users\Trader\AppData\Roaming\Thunderbird\Profiles")
APPROVED_SENDERS = [
    "zacks.com", "wallstwarrior", "beehiiv.com", "traderelite.club",
    "substack.com", "hedgeye.com", "chaikinanalytics.com", "analystratings.net",
    "tradethirsty.net", "protraderstrategies", "wallstreetzen", "freedomincomeoptions",
    "timsykes.com", "TheTradingPub", "thedailyupside",
]

def normalize_dt(dt):
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def scan_diagnostics():
    cutoff = normalize_dt(datetime.now() - timedelta(days=7))
    email_count = 0
    approved_count = 0
    
    for profile in THUNDERBIRD_PROFILES.iterdir():
        if not profile.is_dir():
            continue
        
        mail_root = profile / "Mail"
        if not mail_root.exists():
            continue
        
        for mbox_file in sorted(mail_root.rglob("*")):
            if mbox_file.is_file() and not mbox_file.suffix:
                folder = mbox_file.parent.name
                if "inbox" not in folder.lower() and "spam" not in folder.lower():
                    continue
                
                try:
                    with open(mbox_file, "rb") as f:
                        first_line = f.readline()
                        if not first_line.startswith(b"From "):
                            f.seek(0)
                        
                        while True:
                            try:
                                msg = message_from_binary_file(f)
                                if not msg:
                                    break
                                
                                sender = msg.get("From", "").lower()
                                date_received = normalize_dt(parsedate_to_datetime(msg.get("Date", "")))
                                
                                if date_received < cutoff:
                                    continue
                                
                                email_count += 1
                                
                                # Check if from approved sender
                                is_approved = any(a in sender for a in APPROVED_SENDERS)
                                
                                if is_approved:
                                    approved_count += 1
                                    subject = msg.get("Subject", "")[:60]
                                    print(f"✓ {sender[:45]:45} | {subject}")
                            except:
                                continue
                except:
                    pass
    
    print(f"\nTotal INBOX/SPAM emails (7 days): {email_count}")
    print(f"From approved senders: {approved_count}")

scan_diagnostics()
