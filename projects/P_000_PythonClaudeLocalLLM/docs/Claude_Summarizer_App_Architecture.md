# Claude Summarizer App - Project Architecture

## Overview

A FastAPI application that ingests text or URLs, summarizes content using the Claude API, and stores results for retrieval. Designed for local use within the AI-Agent-Learning-Hub ecosystem.

---

## Project Structure

```
project-root/
- app/
  - main.py                 # FastAPI application & routing
  - api/
    - ingest.py             # Content ingestion (Text/URL)
    - summarize.py          # Claude summarization logic
    - history.py            # State/Log retrieval
  - prompts/
    - summary_v1.txt        # Prompt templates
    - takeaways_v1.txt
  - utils/
    - claude_client.py      # Claude API wrapper
    - chunker.py            # Text splitting for long docs
    - parsers.py            # Cleaning Claude responses
  - models/
    - store.py              # SQLite or in-memory storage
- requirements.txt
- .env                      # ANTHROPIC_API_KEY
```

---

## File Descriptions

- app/main.py - FastAPI entry point. Defines routes and wires the API modules. Run with: uvicorn app.main:app --reload
- app/api/ingest.py - Accepts raw text or a URL; fetches and extracts page content before summarizing.
- app/api/summarize.py - Core logic; calls claude_client.py with the prompt template, handles chunking, returns structured output.
- app/api/history.py - Retrieves past summaries and logs from storage.
- app/prompts/summary_v1.txt - General summarization template (version controlled).
- app/prompts/takeaways_v1.txt - Key-takeaways template for trading articles, research, education.
- app/utils/claude_client.py - Anthropic API wrapper; centralizes key handling, model selection, error handling.
- app/utils/chunker.py - Splits long documents into token-safe chunks.
- app/utils/parsers.py - Cleans and structures raw Claude responses.
- app/models/store.py - SQLite (or in-memory) storage of summaries, timestamps, source references.

---

## Environment Setup

Python: shared Hub conda env p140 -> C:\Users\Trader\.conda\envs\p140\python.exe
API key: store in .env (never commit): ANTHROPIC_API_KEY=your_key_here
.gitignore: .env, __pycache__/, *.pyc, *.db

## Requirements
fastapi, uvicorn, anthropic, python-dotenv, requests, beautifulsoup4
Install: "C:\Users\Trader\.conda\envs\p140\python.exe" -m pip install -r requirements.txt

## Recommended Hub Placement
AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\integrations\claude_api\summarizer_app\

## Status
- [ ] Project structure created
- [ ] Claude API wrapper built and tested
- [ ] Prompt templates written
- [ ] FastAPI routes working
- [ ] Storage layer implemented
- [ ] History retrieval working

---
Last Updated: February 25, 2026 (saved to disk 2026-06-05 from Project knowledge)