# LM Studio Console Suppression — Work Order
**For:** P_000 session
**Date:** 2026-05-30
**Status:** Ready to implement — tested pattern, exact file locations confirmed
**Logged by:** P_300 session (refactor S1 complete)

## Resolution

**LM Studio UI fix (2026-05-30):**
Noise eliminated by toggling off all logging in LM Studio's Developer tab:
1. Developer tab → Developer Logs panel → click `...` (three-dot menu, top right of log panel)
2. **Verbose Logging** → OFF
3. **Redact Content** → OFF
4. **Log Incoming Tokens** → OFF
5. **File Logging Mode** → OFF

Settings persist across LM Studio restarts. No code change required.
Version confirmed working: LM Studio 0.4.15.

**Note:** The `_suppress_to_diag()` context manager in `lms_suppress.py` and
`lm_studio_api.py` does NOT suppress this noise — LM Studio writes directly
to the Windows console handle from its own process. Python stdout/stderr
redirection has no effect on it. The UI toggle is the only effective control.

---

## Problem

LM Studio's server process writes internal diagnostics directly to the
console window whenever any project makes a network call to it:

```
[LMSInternal][LMSAuthenticator][Client=LM Studio][Endpoint=listLoaded] ...
[MultiplexedLLMProvider] Getting model instance info ...
[LLMProvider] Starting prediction for instance: ...
Applying structured output configuration: { "type": "none" }
```

This noise appears in every project's BAT window during eval runs. It cannot
be suppressed from the BAT (it is stdout from the LM Studio server process,
not stderr from Python). It must be suppressed inside the Python layer that
makes the LM Studio calls.

---

## Root Cause

The noise fires during two operations in `lm_studio_api.py`:
1. `get_wrapper_status()` — the status/readiness check (polled repeatedly)
2. `send_chat_request()` — the actual prediction call

Both make async HTTP calls via `httpx`. The LM Studio server responds to
these calls by writing diagnostics to whatever console handle is attached
to the process — which is the calling project's BAT window.

---

## Solution

Wrap ALL async HTTP calls in `lm_studio_api.py` with a stdout/stderr
redirect to `LOG_DIR / "lms_diag.log"` (already defined in `config.py`).

**Key principle:** The fix lives here — in the Hub-level integration — so
every project gets clean console output automatically. No per-project
wiring required. This is the Process Boundary Standard: infrastructure
concerns belong in infrastructure, at the highest applicable level.

The log overwrites each run. If anything goes wrong, inspect:
```
C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\outputs\logs\lms_diag.log
```

---

## Exact Changes Required

### File 1: `config.py`
**Path:** `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\config.py`
**Change:** Add one constant below `LOG_FILE`:

```python
# Diagnostic log for LM Studio server console output (overwrites each run)
LMS_DIAG_LOG = LOG_DIR / "lms_diag.log"
```

That's the only change to `config.py`.

---

### File 2: `lm_studio_api.py`
**Path:** `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\lm_studio_api.py`

**Change 1 — add import at top (after existing imports):**
```python
from integrations.lm_studio.config import (
    ...existing imports...,
    LMS_DIAG_LOG,          # ADD THIS
)
```

**Change 2 — add a context manager helper function** (after the existing
`_wait_for_model_ready` helper, before `get_available_models`):

```python
from contextlib import contextmanager

@contextmanager
def _suppress_to_diag():
    """Redirect stdout/stderr to LMS_DIAG_LOG for the duration of a block.

    LM Studio's server process writes diagnostics to the attached console
    handle during every API call. This context manager captures that output
    in LMS_DIAG_LOG (overwrite each run) so the caller's console stays clean.
    Restores stdout/stderr unconditionally via finally.
    """
    import sys
    LMS_DIAG_LOG.parent.mkdir(parents=True, exist_ok=True)
    saved_out, saved_err = sys.stdout, sys.stderr
    try:
        with open(LMS_DIAG_LOG, "w", encoding="utf-8") as fh:
            sys.stdout = fh
            sys.stderr = fh
            yield
    finally:
        sys.stdout = saved_out
        sys.stderr = saved_err
```

**Change 3 — wrap `get_available_models()`:**
```python
async def get_available_models() -> Optional[Dict[str, Any]]:
    with _suppress_to_diag():
        try:
            async with httpx.AsyncClient(...) as client:
                ...
```

**Change 4 — wrap `_wait_for_model_ready()`** (the polling loop):
```python
async def _wait_for_model_ready(model_id: str) -> bool:
    deadline = ...
    while ...:
        with _suppress_to_diag():
            try:
                async with httpx.AsyncClient(...) as client:
                    ...
```

**Change 5 — wrap `send_chat_request()`** — this is the main one, where
`[MultiplexedLLMProvider] Predicting...` and
`Applying structured output configuration` fire:
```python
async def send_chat_request(...):
    with _suppress_to_diag():
        is_ready = await _wait_for_model_ready(model)
    ...
    with _suppress_to_diag():
        async with httpx.AsyncClient(...) as client:
            response = await client.post(...)
```

**Change 6 — wrap `check_lm_studio_health()`:**
```python
async def check_lm_studio_health() -> bool:
    with _suppress_to_diag():
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                ...
```

**Change 7 — wrap `get_wrapper_status()`** (the status polling):
```python
async def get_wrapper_status(...):
    with _suppress_to_diag():
        is_running = await check_lm_studio_health()
    ...
    with _suppress_to_diag():
        async with httpx.AsyncClient(...) as client:
            ...
```

---

## After This Is Done

### Cleanup in P_300 (after Hub fix confirmed working):
1. `lm_studio_status.py` at `integrations/lm_studio/infrastructure/` can be
   simplified — it no longer needs its own stdout redirect block since
   `lm_studio_api.py` handles it internally. The `check()` function reduces
   to a clean call with no file handle management.

2. `daily_evaluate_pipeline.py` — the `_diag_log` path construction can be
   removed from `main()`. `check()` no longer needs a `diag_log` param.

### Verification
Run `P_300_DailyEval_v2.bat ARLP` (or any symbol with LM Studio running).
Console output should be:

```
=======================================================================
       P_300 DAILY EVALUATE + OBSIDIAN LOG + ARCHIVE
=======================================================================
Symbol  : ARLP
...
========================================================================
P_300 SIGNAL REPORT  ARLP BUY
========================================================================
...
```

No `[LMSInternal]`, no `[MultiplexedLLMProvider]`, no
`Applying structured output configuration`. Clean.

Diagnostic log at:
`C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\outputs\logs\lms_diag.log`

---

## Version Bumps Required
| File | Current | Target |
|------|---------|--------|
| `config.py` | no version | add `LMS_DIAG_LOG` constant only |
| `lm_studio_api.py` | no version header | bump or add changelog entry |

---

## Why This Approach Is Correct

The LM Studio server diagnostics are an infrastructure output-management
concern. They originate inside the LM Studio API layer. The suppression
belongs in the same layer — `lm_studio_api.py` — not in any calling project.

Per the Hub-level Process Boundary Standard (`python-project-architecture`
SKILL): infrastructure change must never require application change.
Once this fix lands in `lm_studio_api.py`, zero project files change.

---

**End of Work Order**
