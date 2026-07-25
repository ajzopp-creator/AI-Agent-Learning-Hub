# LM Studio Integration Guide

**For Any Hub Project Wanting to Talk to Local LLM**

---

## Overview

The LM Studio wrapper provides a **status check function** that any Hub project (P_010, P_300, P_110, etc.) can use to verify the local LLM is ready before attempting to use it.

No code changes required. Just a single status query.

---

## Quick Start (2 lines)

```python
from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status

status = await get_wrapper_status()
```

Then check the response:

```python
if not status['lm_studio_running']:
    print(f"ERROR: {status['action_required']}")
    sys.exit(1)

if status['model_mismatch']:
    print(f"ERROR: {status['action_required']}")
    sys.exit(1)

# All good — ready to use local LLM
```

---

## The Status Dict

`get_wrapper_status()` returns a dict with these keys:

| Key | Type | Meaning |
|---|---|---|
| `lm_studio_running` | bool | Is LM Studio responding? |
| `current_model` | str or None | What model is loaded now? |
| `expected_model` | str | What model we want (primary) |
| `model_mismatch` | bool | Is the wrong model loaded? |
| `action_required` | str or None | If there's a problem, what to do |
| `message` | str | Human-readable status summary |

---

## Example: Status = Ready

```python
{
    'lm_studio_running': True,
    'current_model': 'deepseek-r1-distill-qwen-14b',
    'expected_model': 'deepseek-r1-distill-qwen-14b',
    'model_mismatch': False,
    'action_required': None,
    'message': 'Ready — deepseek-r1-distill-qwen-14b is loaded and operational'
}
```

---

## Example: Status = LM Studio Not Running

```python
{
    'lm_studio_running': False,
    'current_model': None,
    'expected_model': 'deepseek-r1-distill-qwen-14b',
    'model_mismatch': True,
    'action_required': 'LM Studio is not running. Launch: C:\\Program Files\\LM Studio\\LM Studio.exe',
    'message': 'LM Studio not responding'
}
```

---

## Example: Status = Wrong Model Loaded

```python
{
    'lm_studio_running': True,
    'current_model': 'llama-4-scout-17b-16e-instruct',
    'expected_model': 'deepseek-r1-distill-qwen-14b',
    'model_mismatch': True,
    'action_required': 'Wrong model loaded. Load: deepseek-r1-distill-qwen-14b (currently: llama-4-scout-17b-16e-instruct)',
    'message': 'Model mismatch: llama-4-scout-17b-16e-instruct'
}
```

---

## Design Philosophy

- **Zero side effects** — Status check only reads state, never changes anything
- **Clear instructions** — If something's wrong, operator knows exactly what to do
- **Minimal integration** — Projects don't need to import the full client, manage async loops, or change their core logic
- **Pre-flight check only** — Call once at startup, not in trading loops

---

## File Location

**Status function:** `integrations/lm_studio/infrastructure/lm_studio_api.py`

**Import:** 
```python
from integrations.lm_studio.infrastructure.lm_studio_api import get_wrapper_status
```

---

## When to Call

Call `get_wrapper_status()` once at your project's startup. If there's a problem, exit cleanly and let the operator fix it.

```python
async def main():
    # Pre-flight check
    status = await get_wrapper_status()
    if status['model_mismatch'] or not status['lm_studio_running']:
        print(f"Cannot continue: {status['action_required']}")
        sys.exit(1)
    
    # Project continues normally
    ...
```

---

## Future: From Status Check to Active Use

Once the operator confirms LM Studio is ready, projects will use the full client to send prompts and get responses. But that's a **separate integration** — status check is just the pre-flight step.

---

Last Updated: 2026-05-28