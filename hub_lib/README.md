# hub_lib

Shared model-routing facade for the AI-Agent-Learning-Hub.

## What it does
Decouples your projects from specific model IDs and providers. Call
`ModelManager.generate("vp_pattern", prompt)` without knowing or caring
whether that task routes to LM Studio, Claude, or Gemini today.

## Install (one time, into the p140 conda env)

Open an Anaconda prompt and run:

```
conda activate p140
pip install -e C:\Users\Trader\AI-Agent-Learning-Hub\hub_lib[all]
```

The `-e` flag is "editable install" — edits to hub_lib code take effect
immediately, no reinstall needed.

The `[all]` extra pulls in `openai`, `anthropic`, and `google-genai`.
If you only need one provider, swap `[all]` for `[lmstudio]`,
`[anthropic]`, or `[google]`.

## Configure

The Hub already has a comprehensive `.env.example` at the Hub root.
hub_lib reads from `C:\Users\Trader\AI-Agent-Learning-Hub\.env` if it
exists. Make sure it contains:

```
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
```

If you don't yet have a `.env`, copy the root template:

```
copy C:\Users\Trader\AI-Agent-Learning-Hub\.env.example C:\Users\Trader\AI-Agent-Learning-Hub\.env
```

## Use from any project

```python
from hub_lib import ModelManager, verify_health, load_hub_env

load_hub_env()
verify_health(["vp_pattern"])              # canary — once per session
text = ModelManager.generate("vp_pattern", "Analyze this chart pattern...")
```

## Add a new task
Edit `hub_lib\model_manager.py` and add a row to `MODEL_MAP`:

```python
"my_new_task": ("anthropic", "claude-opus-4-7"),
```

Or override at runtime without touching code, via `.env`:

```
HUBLIB_TASK_MY_NEW_TASK=google:gemini-2.5-pro
```

## Tasks shipped with V0.1

| Task | Provider | Model |
|---|---|---|
| `local_fast`    | lmstudio  | qwen2.5-7b-instruct |
| `local_smart`   | lmstudio  | qwen2.5-32b-instruct |
| `cloud_fast`    | anthropic | claude-haiku-4-5-20251001 |
| `cloud_smart`   | anthropic | claude-opus-4-7 |
| `vp_pattern`    | google    | gemini-2.5-flash |
| `vp_reasoning`  | google    | gemini-2.5-pro |
