# Claude-Python Agentic Migration Plan (MVP)

Reference: https://github.com/Krigsexe/agentic-workflow (README)

## 1. Project Overview
Transition a standard Claude integration into an agentic workflow using a modular Python (FastAPI) structure.

## 2. Directory Structure
```
project-root/
- app/
  - __init__.py
  - main.py                 # FastAPI application & routing
  - api/
    - ingest.py             # Content ingestion (Text/URL)
    - summarize.py          # Logic for Claude summarization
    - history.py            # State/Log retrieval
  - prompts/
    - summary_v1.txt        # Prompt templates
    - takeaways_v1.txt
  - utils/
    - claude_client.py      # Claude API wrapper
    - chunker.py            # Text splitting for long docs
    - parsers.py            # Cleaning Claude's response
  - models/
    - store.py              # SQLite or In-memory storage
- requirements.txt          # fastapi, uvicorn, httpx
- .env                      # ANTHROPIC_API_KEY
```

## 3. Core Requirements (requirements.txt)
fastapi
uvicorn[standard]
httpx
pydantic-settings
python-dotenv

## 4. MVP Core Logic

A. API Ingestion (app/api/ingest.py)
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class IngestRequest(BaseModel):
    content: str
    metadata: dict = {}

@router.post("/")
async def ingest_content(data: IngestRequest):
    # logic to store content in a database/file
    return {"status": "success", "msg": "Content ingested for processing"}
```

B. Summarization Orchestrator (app/api/summarize.py)
```python
from fastapi import APIRouter
from app.utils.claude_client import call_claude
from app.utils.chunker import split_text

router = APIRouter()

@router.post("/{task_id}")
async def run_summary(task_id: str):
    # 1. Fetch content from store
    # 2. If long, split into chunks
    # 3. For each chunk, call Claude with prompt_template
    # 4. Merge results
    return {"summary": "...", "takeaways": []}
```

## 5. Recommended Prompt Template (app/prompts/summary_v1.txt)
```
System: You are an expert research assistant.
Task: Summarize the following text provided by the user.
Constraints:
- Use 3-5 bullet points.
- Highlight actionable takeaways.
- Provide a 1-sentence executive summary at the end.

Text to summarize:
{{content}}
```

## 6. Next Steps for Migration
1. Environment Setup: use the shared p140 conda env; install dependencies.
2. Move Prompts: extract existing Claude prompts from hardcoded strings into /prompts.
3. Refactor Client: move Claude calling logic into app/utils/claude_client.py.
4. Test End-to-End: use the FastAPI Swagger UI (/docs) to test Ingest -> Summarize -> View Result.

---
Saved to disk 2026-06-05 from Project knowledge (trailing clipboard cruft removed).