# P_800 Vault Interface — Integration Guide

**File:** `shared_resources/python_utils/VAULT_INTERFACE_README.md`
**Owner:** P_800 (Automation Note-Taking & Knowledge Building)
**Last Updated:** 2026-05-22

---

## What It Does

The vault interface is a single Python function that writes a structured note
to the AJZ Strategies Obsidian vault. The sending project passes a schema name
and a data dictionary. P_800 handles validation, YAML frontmatter generation,
file naming, folder routing, and the disk write.

The sending project needs zero knowledge of Obsidian or the vault structure.

---

## Import

```python
from shared_resources.python_utils.vault_interface import write_to_vault
```

If `shared_resources` is not already on your Python path, add this before the import:

```python
import sys
sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils")
sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts")
```

---

## Function Signature

```python
write_to_vault(
    schema_name: str,       # which schema to use — see list below
    data: dict,             # field values to write
    body: str = "",         # optional text block below frontmatter
    overwrite: bool = True  # False = skip if note already exists
) -> bool                   # True = written, False = skipped
```

---

## Schema Names & Key Fields

### `"P115"` — Trade Evaluation (P_115 Buy the Dip)

**Required:** `date`, `symbol`
**Common fields:** `step1_verdict`, `setup_score`, `traded`, `outcome`, `why_code`, `sig_code`

```python
write_to_vault("P115", {
    "date": "2026-05-22",
    "symbol": "AAPL",
    "step1_verdict": "BUY",
    "setup_score": 5,
    "traded": "N",
    "account_balance": 32812,
})
```

---

### `"P300"` — Statistical Signal (P_300 VantagePoint Pattern)

**Required:** `date`, `ticker`
**Common fields:** `signal`, `signal_horizon`, `h5_win_rate`, `h5_mean_ret`, `n_matches`
**`body` param:** pass the full TXT narrative block here

```python
write_to_vault("P300", {
    "date": "2026-05-20",
    "ticker": "BAC",
    "signal": "PASS",
    "signal_horizon": 5,
    "h5_win_rate": 0.60,
    "h5_mean_ret": 2.07,
    "h10_win_rate": 0.60,
    "n_matches": 20,
}, body=report_text)   # report_text = full TXT file contents
```

---

### `"P020"` — Trade Performance (P_020 Performance Analysis)

**Required:** `date`, `symbol`
**Common fields:** `account_id`, `system`, `realized_pnl`, `realized_R`, `outcome`, `why_code`, `sig_code`
**Note:** `date` should be the close date.

```python
write_to_vault("P020", {
    "date": "2026-05-15",        # close_date
    "symbol": "AMR",
    "account_id": "AJZ6348",
    "system": "P_115",
    "why_code": "BTD",
    "sig_code": "A",
    "open_date": "2026-05-10",
    "close_date": "2026-05-15",
    "entry_price": 42.30,
    "exit_price": 45.10,
    "realized_pnl": 280.00,
    "realized_R": 1.87,
    "outcome": "TP Hit",
    "days_held": 5,
})
```

---

### `"P400"` — Trade Lifecycle (P_400 Trade Management)

**Required:** `date`, `ticker`
**Common fields:** `council_verdict`, `lifecycle_status`, `entry_price`, `stop_price`, `why_code`
**`body` param:** pass the TOS narrative block here

```python
write_to_vault("P400", {
    "date": "2026-05-22",
    "ticker": "NVDA",
    "account_id": "AJZ6348",
    "council_verdict": "Approve",
    "lifecycle_status": "OPEN",
    "entry_price": 112.50,
    "stop_price": 108.00,
    "why_code": "BTD",
    "sig_code": "B",
}, body=tos_narrative_text)
```

---

### `"KB"` — Knowledge Base (Articles & Research)

**Required:** `date`, `title`
**Common fields:** `kb_type`, `origin`, `tags`, `ticker_relevance`, `sector`

```python
write_to_vault("KB", {
    "date": "2026-05-22",
    "title": "Fed Rate Impact on Regional Banks",
    "kb_type": "Article",
    "origin": "Web Clipper",
    "ai_summarized": True,
    "tags": ["macro", "banking", "rates"],
    "ticker_relevance": ["BAC", "JPM"],
    "sector": "Financials",
})
```

---

## What P_800 Handles Automatically

- Field validation against the schema (missing required fields raise `ValueError`)
- Defaulting all optional fields to `null` in the YAML frontmatter
- Generating the correct filename (`YYYY-MM-DD_SYMBOL.md`)
- Routing to the correct vault folder (`TradeManagement/P115/`, etc.)
- Creating the `.md` file and any missing parent directories
- Logging all writes to `P_800_Automation_Note_Taking/logs/vault_interface.log`

---

## Error Handling

```python
from vault_interface import write_to_vault

try:
    write_to_vault("P115", data)
except ValueError as e:
    # Unknown schema name OR required field missing OR type mismatch
    print(f"Data error: {e}")
except OSError as e:
    # Disk write failed (permissions, vault path missing, etc.)
    print(f"Write error: {e}")
```

---

## File Locations

| Resource | Path |
|----------|------|
| Public API | `shared_resources\python_utils\vault_interface.py` |
| This guide | `shared_resources\python_utils\VAULT_INTERFACE_README.md` |
| Engine (internal) | `P_800_Automation_Note_Taking\scripts\obsidian_writers\` |
| Vault folder | `trading_journal\TradeManagement\` |
| Write log | `P_800_Automation_Note_Taking\logs\vault_interface.log` |

---

*Questions or schema changes: raise in a P_800 session. P_800 owns the schemas.*
