"""
P_805 Email Trade Extractor v2 - Whitelist senders from CSV, flexible ticker matching
"""

import re
import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta, date, timezone
from email import message_from_binary_file
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

# Configuration
THUNDERBIRD_PROFILES = Path(r"C:\Users\Trader\AppData\Roaming\Thunderbird\Profiles")
TARGET_FOLDERS = ["INBOX", "Inbox", "Spam", "spam", "Junk", "junk"]
EXCLUDED_SENDERS = ["impens", "andreessen", "gaud"]

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "daily"
SENDER_SHEET = Path(__file__).parent.parent / "data" / "sender_sheet.csv"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ticker pattern: 1-5 uppercase letters, with word boundary
# Matches: TSLA, AAPL, BRK, etc. but avoids HTML tags
TICKER_PATTERN = r"\b([A-Z]{1,5})\b"

# Common non-ticker words to exclude (HTML, articles, prepositions, etc.)
NON_TICKERS = {
    "HTML", "HEAD", "BODY", "META", "HREF", "TYPE", "CLASS", "STYLE",
    "HTTPS", "HTTP", "ABOUT", "CLICK", "HERE", "LINK", "WHEN", "WHICH",
    "THAT", "THIS", "WITH", "HAVE", "FROM", "THAN", "WERE", "WILL",
    "BEEN", "ARE", "WAS", "THE", "AND", "FOR", "BUT", "NOT", "YOU",
    "CAN", "ITS", "MAY", "NEW", "NOW", "WAY", "WHO", "OUR", "OUT",
    "DAY", "GET", "HAS", "HIM", "HIS", "HOW", "ITS", "LET", "PUT",
    "SAY", "SHE", "TOO", "USE", "HER", "YOUR", "JUST", "TIME",
    "EMAIL", "MESSAGE", "IMAGE", "PROPERTY", "CONTENT", "VALUE",
    "PERTY", "CLUB", "EIGHT", "DOCTYPE", "CHARSET", "CHARSET", "EQUIV",
    "GMT", "UTC", "EST", "PST", "CST", "MST", "EDT", "CDT", "MDT", "PDT",
}

SCAN_HOURS = 24

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_text(self):
        return ' '.join(self.text)

def strip_html(html):
    """Remove HTML tags from text"""
    try:
        stripper = HTMLStripper()
        stripper.feed(html)
        return stripper.get_text()
    except:
        return html

def load_enabled_senders():
    """Load sender whitelist from CSV"""
    senders = set()
    if not SENDER_SHEET.exists():
        print(f"WARNING: Sender sheet not found: {SENDER_SHEET}")
        return senders
    
    try:
        with open(SENDER_SHEET, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("enabled", "").lower() == "true":
                    senders.add(row["email_address"].lower())
    except Exception as e:
        print(f"Error loading sender sheet: {e}")
    
    return senders

def extract_tickers(text):
    """Extract stock tickers - flexible, filter out common non-tickers"""
    matches = re.findall(TICKER_PATTERN, text.upper())
    # Filter out non-tickers
    tickers = [t for t in matches if t not in NON_TICKERS and len(t) >= 1]
    return list(set(tickers))

def extract_thesis(text):
    """Extract core thesis from email"""
    sentences = re.split(r"[.!?]+", text)
    for sent in sentences:
        s = sent.strip()
        if 20 < len(s) < 300:
            return s[:150]
    return None

def normalize_datetime(dt):
    """Handle naive/aware datetimes"""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def is_target_folder(folder_path):
    """Check if folder is INBOX or SPAM"""
    folder_name = folder_path.name if hasattr(folder_path, 'name') else str(folder_path)
    return any(target.lower() in folder_name.lower() for target in TARGET_FOLDERS)

def scan_mbox_files(enabled_senders):
    """Scan INBOX/SPAM for emails from whitelist senders"""
    cutoff_time = normalize_datetime(datetime.now() - timedelta(hours=SCAN_HOURS))
    emails = []
    
    if not THUNDERBIRD_PROFILES.exists():
        print(f"ERROR: Thunderbird folder not found")
        return emails
    
    print(f"Monitoring {len(enabled_senders)} senders from sender_sheet.csv\n")
    
    for profile in THUNDERBIRD_PROFILES.iterdir():
        if not profile.is_dir():
            continue
        
        mail_root = profile / "Mail"
        if not mail_root.exists():
            continue
        
        # Find INBOX/SPAM folders only
        for mbox_file in sorted(mail_root.rglob("*")):
            if mbox_file.is_file() and not mbox_file.suffix:
                if not is_target_folder(mbox_file.parent):
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
                                
                                sender_raw = msg.get("From", "").lower()
                                subject = msg.get("Subject", "")
                                
                                # Check whitelist
                                if not any(s in sender_raw for s in enabled_senders):
                                    continue
                                
                                # Skip excluded
                                if any(ex in sender_raw for ex in EXCLUDED_SENDERS):
                                    continue
                                
                                try:
                                    date_received = normalize_datetime(parsedate_to_datetime(msg.get("Date", "")))
                                except:
                                    date_received = normalize_datetime(None)
                                
                                if date_received < cutoff_time:
                                    continue
                                
                                # Extract body
                                body = ""
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() == "text/plain":
                                            try:
                                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                                break
                                            except:
                                                pass
                                else:
                                    try:
                                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    except:
                                        body = msg.get_payload()
                                
                                # Strip HTML
                                body = strip_html(body)
                                
                                # Extract tickers
                                tickers = extract_tickers(f"{subject} {body}")
                                
                                if tickers:
                                    emails.append({
                                        "sender": sender_raw,
                                        "subject": subject,
                                        "body": body,
                                        "date": date_received,
                                        "tickers": tickers,
                                    })
                                    ticker_str = ", ".join(sorted(tickers)[:5])
                                    print(f"✓ {sender_raw[:45]:45} | {ticker_str}")
                            
                            except Exception as e:
                                continue
                
                except Exception as e:
                    pass
    
    return emails

def main():
    print("="*70)
    print("P_805 Email Trade Extractor v2 - Whitelist Scan")
    print("="*70)
    
    enabled_senders = load_enabled_senders()
    if not enabled_senders:
        print("ERROR: No enabled senders in sender_sheet.csv")
        return
    
    emails = scan_mbox_files(enabled_senders)
    
    if not emails:
        print("\nNo emails found with stock tickers in INBOX/SPAM (last 24h)")
        return
    
    # Parse trades
    trades = []
    for email in emails:
        for ticker in email["tickers"]:
            trade = {
                "date": email["date"].date(),
                "ticker": ticker,
                "price_context": None,
                "catalyst_date": None,
                "core_thesis": extract_thesis(email["body"]),
                "key_metric": None,
                "smart_money": None,
                "risk_red_flag": None,
                "lead_type": "Primary",
                "source": email["sender"].split("@")[0] if "@" in email["sender"] else email["sender"],
            }
            trades.append(trade)
    
    print(f"\n{'-'*70}")
    print(f"Found {len(emails)} emails with {len(trades)} total ticker mentions\n")
    
    # Write CSV
    if trades:
        output_file = OUTPUT_DIR / f"{date.today().isoformat()}_trades.csv"
        headers = ["date", "ticker", "price_context", "catalyst_date", "core_thesis", "key_metric", "smart_money", "risk_red_flag", "lead_type", "source"]
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(trades)
        
        print(f"✓ Wrote {output_file}")
        print(f"  Ready for review in Excel")

if __name__ == "__main__":
    main()
