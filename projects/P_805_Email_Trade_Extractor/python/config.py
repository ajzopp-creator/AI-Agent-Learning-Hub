"""P_805 configuration — paths, thresholds, parameters.

Per the Hub-wide python-project-architecture standard: all constants live
here and are imported by any layer that needs a value. No hardcoded paths
or values exist in domain/, infrastructure/, or application/ modules.

HUB_ROOT is the only hardcoded filesystem path allowed in this project.
All other project paths are derived from it.
"""

from pathlib import Path

# ── PATH CONFIGURATION ────────────────────────────────────────────────────────
# Hub root — only hardcoded path allowed per architecture standard.
HUB_ROOT: Path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")

# Project paths (derived)
PROJECT_ROOT: Path = HUB_ROOT / "projects" / "P_805_Email_Trade_Extractor"
DATA_DIR: Path = PROJECT_ROOT / "data"
DATA_DAILY_DIR: Path = DATA_DIR / "daily"
DATA_MONTHLY_DIR: Path = DATA_DIR / "monthly"
SENDER_SHEET: Path = DATA_DIR / "sender_sheet.csv"
LOGS_DIR: Path = PROJECT_ROOT / "python" / "logs"

# ── THUNDERBIRD CONFIGURATION ─────────────────────────────────────────────────
# Live Thunderbird profile. Confirmed 2026-04-26 by check_ietimport_dates.py:
# all four IMAP INBOX caches (Yahoo, Gmail, iCloud, Outlook) are current and
# receiving live mail under m306ztzh.IETimport, NOT 2slie5gz.default-release.
# The "-1" suffix on imap.gmail-1.com / imap.mail.me-1.com is Thunderbird's
# disambiguation when the same hostname appears in multiple account configs;
# do not strip it.
THUNDERBIRD_ROOT: Path = Path(r"C:\Users\Trader\AppData\Roaming\Thunderbird\Profiles")
PROFILE_PATH: str = "m306ztzh.IETimport"
PROFILE_ROOT: Path = THUNDERBIRD_ROOT / PROFILE_PATH

# Thunderbird splits mail across two subdirectories:
#   Mail\     — Local Folders (archived POP mail, user-created folders)
#   ImapMail\ — Live IMAP inbox caches (one dir per server)
MAIL_ROOT: Path = PROFILE_ROOT / "Mail"
IMAP_ROOT: Path = PROFILE_ROOT / "ImapMail"

# ── ACCOUNT MAP ───────────────────────────────────────────────────────────────
MBOX_FILES: dict[str, str] = {
    "icloud":  r"ImapMail\imap.mail.me-1.com\INBOX",
    "gmail":   r"ImapMail\imap.gmail-1.com\INBOX",
    "outlook": r"ImapMail\outlook.office365.com\INBOX",
    "yahoo":   r"ImapMail\imap.mail.yahoo.com\INBOX",
}
IMAP_ACCOUNT_ORDER: list[str] = ["icloud", "gmail", "outlook", "yahoo"]

# ── EXTRACTION DESTINATION (Phase 2+) ─────────────────────────────────────────
EXTRACTED_FOLDER_NAME: str = "ExtractedNewsletterFolder"
EXTRACTED_FOLDER_AUTOCREATE: bool = True

# ── SCAN PARAMETERS ───────────────────────────────────────────────────────────
SCAN_DAYS: int = 30
CONSENSUS_THRESHOLD: int = 2

# ── LOGGING ───────────────────────────────────────────────────────────────────
LOG_FILE: Path = LOGS_DIR / "p805.log"
REJECT_LOG_FILE: Path = LOGS_DIR / "rejected.log"
LOG_LEVEL_CONSOLE: str = "INFO"
LOG_LEVEL_FILE: str = "DEBUG"
LOG_MAX_BYTES: int = 5_000_000
LOG_BACKUP_COUNT: int = 3

# ── PHASE 3: TICKER EXTRACTION ────────────────────────────────────────────────
# Patterns are tried in order. Each pattern's regex MUST have exactly ONE
# capturing group, which is the ticker. To add a new pattern, append a dict
# here — no code changes elsewhere. Confidence is just a label that gets
# carried into the output CSV; sort/filter on it downstream.
TICKER_PATTERNS: list[dict] = [
    {
        "name": "exchange_paren",
        "regex": r"\((?:NYSE|NASDAQ|Nasdaq|NYSE\s+American|AMEX|OTC)\s*:\s*([A-Z]{1,5})\)",
        "confidence": "high",
        "description": "(NYSE: ROLR), (Nasdaq: ACON), (NYSE American: ROLR)",
    },
    {
        "name": "cashtag",
        "regex": r"\$([A-Z]{1,5})\b",
        "confidence": "high",
        "description": "$TSLA, $AAPL — Twitter/Stocktwits convention",
    },
    {
        "name": "wsz_url",
        "regex": r"wallstreetzen\.com/stocks/us/(?:nyse|nasdaq)/([a-z]{1,5})\b",
        "confidence": "high",
        "description": "WallStreetZen URL paths — ticker is last segment, lowercased",
    },
    {
        "name": "bare_paren",
        "regex": r"\b\(([A-Z]{1,5})\)",
        "confidence": "medium",
        "description": "(TSLA), (AAPL) — bare ticker in parens; needs blocklist",
    },
]

# Words that look like parenthesized tickers but aren't. Applies ONLY to
# matches from patterns whose name contains 'paren' (extension point).
BARE_PAREN_BLOCKLIST: set[str] = {
    "CEO", "CFO", "COO", "CTO", "CMO", "VP", "USA", "PDF", "EST", "EDT",
    "CST", "CDT", "PST", "PDT", "MST", "MDT", "GMT", "UTC", "LLC", "INC",
    "LTD", "IPO", "ETF", "URL", "FAQ", "FYI", "NA", "USD", "EUR", "GBP",
    "JPY", "AI", "ML", "AR", "VR", "VC", "PE", "NEW", "OLD", "FROM", "TO",
    "PM", "AM", "ET", "Q1", "Q2", "Q3", "Q4", "ESG", "FOMC", "CPI", "GDP",
    "PPI", "DOE", "DOJ", "FBI", "SEC", "FDA", "FCC", "NASA", "OPEC",
}

# Direction inference: search a window around each ticker for these keywords.
# Add keywords here without touching code. First matching bucket wins; ties
# resolve in dict-iteration order (long → short → watch).
DIRECTION_KEYWORDS: dict[str, list[str]] = {
    "long": [
        # Standard
        "buy", "long", "bullish", "accumulate", "breakout", "upside",
        "strong buy", "outperform", "overweight", "rally", "surge",
        "uptrend", "calls", "going long",
        # Newsletter-typical price-action verbs
        "ripped", "soared", "popped", "jumped", "climbed", "spiked",
        "exploded", "screamed", "roared", "blasted", "gapped up",
        "higher", "gained", "bounced", "recovered", "lifted",
    ],
    "short": [
        # Standard
        "short", "sell", "bearish", "downside", "avoid", "puts",
        "underperform", "underweight", "downgrade", "tumble", "crash",
        "downtrend", "going short",
        # Newsletter-typical price-action verbs
        "cratered", "tumbled", "tanked", "plunged", "collapsed",
        "dropped", "fell", "slid", "dumped", "flushed", "gapped down",
        "lower", "lost", "declined", "weakened", "sold off",
    ],
    "watch": [
        "watch", "watching", "watchlist", "eye", "monitor", "track",
        "tracking", "keep an eye",
    ],
}
DIRECTION_WINDOW_CHARS: int = 500  # Chars before+after ticker to scan
RAW_CONTEXT_CHARS: int = 500       # Chars stored in TickerSignal.raw_context

# Per-sender max tickers per email. Applies after _best_per_ticker() in
# phase3_extract.py. Keyed by full sender address (lowercase). Senders that
# blast large earnings calendars or watchlists get a cap to reduce noise.
# Add entries here; no code changes needed elsewhere.
SENDER_MAX_TICKERS: dict[str, int] = {
    "newsletter@thedailyrip.stocktwits.com": 5,
}

# Senders to exclude even though they're on the approved list (e.g.,
# personal contacts whose names look like tickers when uppercased).
# Substring match, case-insensitive — "impens" matches "JOHN IMPENS <...>".
EXCLUDED_SENDER_SUBSTRINGS: list[str] = ["impens", "andreessen", "gaud"]

# Phase 3 output file pattern. {date} is replaced with today's ISO date.
DAILY_OUTPUT_CSV: str = "{date}_signals.csv"

# ── KB INTEGRATION (P_805 → P_800 Obsidian Interface) ────────────────────────
# Path wiring to P_800 write handler (required before first KB write)
import sys
import os
P800_SCRIPTS: str = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts"
if P800_SCRIPTS not in sys.path:
    sys.path.insert(0, P800_SCRIPTS)

# KB processing modes
KB_MODE: str = os.getenv("KB_MODE", "full")  # "full" or "summary"
KB_LOOKBACK_DAYS: int = int(os.getenv("KB_LOOKBACK_DAYS", "7"))
KB_INBOX_DIR: Path = PROJECT_ROOT / "data" / "inbox"

# Filename patterns for per-file mode override
KB_MODE_PATTERN_FULL: str = r"--full\.eml$"
KB_MODE_PATTERN_SUMMARIZE: str = r"--summarize\.eml$"

# LM Studio configuration
LM_STUDIO_URL: str = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL: str = "qwen2.5-7b-instruct"
LM_STUDIO_TEMP: float = 0.3
LM_STUDIO_MAX_TOKENS: int = 300
LM_STUDIO_TIMEOUT: int = 60

# ── LLM PRIORITY ──────────────────────────────────────────────────────────────
LLM_PRIMARY: str = "Gemini"
LLM_FALLBACK: str = "LM Studio"

# Gemini configuration
GEMINI_MODEL: str = "gemini-2.5-flash"

# Phase 4 ranked output filename pattern
DAILY_RANKED_CSV: str = "{date}_ranked.csv"

# ── IMAP MOVE (Phase 5.3) ─────────────────────────────────────────────────────────────
# Real server-side move of successfully-extracted messages into
# EXTRACTED_FOLDER_NAME via IMAP (not local mbox cache surgery — mbox edits
# don't survive Thunderbird resync and don't move anything on the actual
# server). Credentials are NEVER stored here — retrieved at runtime via
# keyring from Windows Credential Manager, keyed by
# (KEYRING_SERVICE_NAME, account). Set up once per account with:
#   keyring.set_password(KEYRING_SERVICE_NAME, "<account>", "<app password>")
KEYRING_SERVICE_NAME: str = "p805_imap"

IMAP_SERVERS: dict[str, tuple[str, int]] = {
    "icloud":  ("imap.mail.me.com", 993),
    "gmail":   ("imap.gmail.com", 993),
    "outlook": ("outlook.office365.com", 993),
    "yahoo":   ("imap.mail.yahoo.com", 993),
}

# IMAP login addresses. Not secret (the password is what lives in keyring).
IMAP_USERNAMES: dict[str, str] = {
    "icloud":  "tzoppi@icloud.com",
    "gmail":   "ajzopp@gmail.com",
    "outlook": "ajzopp@outlook.com",
    "yahoo":   "ajzopp@yahoo.com",
}

# Safety default (confirmed with Tony 2026-07-14). True = connect, search,
# log what would move, move nothing. Flip to False only after reviewing a
# dry-run log.
# LIVE as of 2026-07-14 after a clean all-account dry-run (Moved=0 DryRun=18
# NotFound=1 Failed=0) — confirmed with Tony before flipping.
MOVE_DRY_RUN: bool = False

IMAP_CONNECT_TIMEOUT: int = 30

# Audit/idempotency log — one row per message actually (or would-be) moved.
# Read before every move run so already-moved messages are never retried.
MOVED_LOG_PATH: Path = DATA_DIR / "moved_messages.csv"

# Accounts excluded from Phase 5.3 IMAP move (Entry 011, 2026-07-14).
# 'outlook' is OAuth2-only in this Microsoft 365 tenant — Basic Auth
# (plain IMAP LOGIN with an app password) is rejected server-side with a
# generic 'AUTHENTICATE failed', regardless of credential correctness.
# Thunderbird itself uses OAuth2 for this account (see its Server Settings).
# Building OAuth2 support (msal + browser consent + token cache) is real
# scope, deferred. Outlook mail is still fully scanned/extracted by Phase 3
# (mbox read, unaffected) — it just never gets auto-filed to
# ExtractedNewsletterFolder; those messages stay in Inbox.
MOVE_SKIP_ACCOUNTS: set[str] = {"outlook"}
