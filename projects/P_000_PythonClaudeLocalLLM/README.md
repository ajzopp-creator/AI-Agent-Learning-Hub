# P_000 - Python, Claude & Local LLM Learning Hub

## Project Purpose

This is the **foundation project** for the AI-Agent-Learning-Hub. It serves five roles:

1. **Python Learning Lab** - A safe sandbox to learn and test Python concepts before applying them to live trading projects
2. **Claude API Integration** - Test and develop code that connects to Anthropic's Claude API
3. **LM Studio / Local LLM Testing** - Build and validate local LLM workflows using LM Studio (Llama models) without cloud dependencies
4. **Reusable Script Library** - Store proven, working scripts that other projects (P_010, P_020, P_300, etc.) can pull from
5. **Master Project Architecture Reference** - This project defines the folder structure, environment standards, and conventions used across the entire Hub

---

## Folder Structure

```
P_000_PythonClaudeLocalLLM/
|
+-- python/                  # Scripts and code examples
+-- tos_scripts/             # Any ThinkScript utilities
+-- data/
|   +-- xml_exports/         # TOS grid exports for testing
|   +-- processed/           # Cleaned/processed data
|   +-- historical/          # Historical reference data
+-- outputs/
|   +-- reports/             # Generated reports
|   +-- charts/              # Visualizations
|   +-- alerts/              # Alert outputs
+-- integrations/
|   +-- lm_studio/           # LM Studio connection scripts and prompts
|   +-- claude_api/          # Claude API test scripts and examples
+-- docs/
    +-- notes/               # Learning notes and discoveries
    +-- examples/            # Working code examples for reference
```

---

## Python Environment

All scripts use the shared conda environment **p140**.

- **Python executable:** `C:\Users\Trader\.conda\envs\p140\python.exe`
- Run scripts from batch files or VS Code using p140 — no venv activation needed
- See `Trading_Projects_Folder_Architecture.md` at the Hub root for full environment documentation

---

## LM Studio Configuration

- **Model in use:** llama-4-scout-17b-16e-instruct
- **API endpoint:** http://localhost:1234/v1
- **Priority:** Local processing preferred over cloud for privacy and cost

---

## Claude API Notes

- API calls are tested here before being integrated into production projects
- Store no API keys in code — use .env files (gitignored)
- Reference `integrations\claude_api\` for working connection examples

---

## Architecture Role

P_000 is numbered **000** intentionally — it is the first project, the reference point.
When building new projects, look here first for:
- Folder structure conventions
- Batch file templates
- Python environment standards
- Reusable utility scripts

---

## Related Projects

| Project | Description |
|---|---|
| P_010_Current_Market_Posture | Daily/intraday market posture analysis |
| P_020_AJZStrategies_PerformanceAnalysisSystem | Account performance tracking |
| P_115_BuytheDipTradingSystem | Buy the dip trading strategy |
| P_300_Vantage_Point_Pattern_Recognition | VantagePoint pattern recognition |

---

## Last Updated
February 23, 2026
