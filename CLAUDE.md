# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands assume CWD is `rag_agent_demo/` and the venv is activated (`source .venv/bin/activate`).

**One-time setup (creates `data/sample.db` and `chroma_db/`):**
```bash
pip install -r requirements.txt
cp .env.example .env       # then fill in ANTHROPIC_API_KEY (and optionally TAVILY_API_KEY)
python data/init_db.py     # build SQLite sample data
python -m src.ingestion    # embed data/docs/*.{md,txt} into ChromaDB
```

**Run:**
```bash
python cli.py                          # interactive CLI (commands: /reset, /quit)
uvicorn src.api:app --reload           # FastAPI server on :8000, Swagger at /docs
```

**Test (no LLM calls — pure tool smoke tests):**
```bash
pytest tests/ -v
pytest tests/test_agent.py::test_sql_select_employees -v   # single test
```

`tests/test_agent.py::setup_module` calls `init_db.init()`, so tests rebuild `data/sample.db` automatically — no separate fixture step needed.

**Reset all generated state:**
```bash
rm -rf chroma_db data/sample.db && python data/init_db.py && python -m src.ingestion
```

## Architecture

This is an **Agentic RAG** demo: Claude (`claude-sonnet-4-6` by default) is the decision core and chooses which of four tools to call to answer each question. Routing is **not** rule-based — it lives in the LLM, steered by tool docstrings and `SYSTEM_PROMPT` in `src/agent.py`.

**Core flow (`src/agent.py`):**
- `RagAgent` keeps a `dict[session_id, AgentExecutor]`. Each session has its own `ConversationBufferMemory` so multi-turn follow-ups (e.g. "now multiply that by 1.15") work.
- `session_id=None` → stateless single-turn (used by `/api/ask`); a non-None id → per-session memory (used by `/api/chat`, CLI uses fixed id `"cli-default"`).
- Built with LangChain's `create_tool_calling_agent` + `AgentExecutor(verbose=True, max_iterations=8)`.
- The `output` from `AgentExecutor.invoke` may come back as a list of content blocks (Anthropic format); `RagAgent.ask` flattens it back to a string.

**Tools (`src/tools/`, registered in `src/tools/__init__.py::ALL_TOOLS`):**
- `search_documents` — ChromaDB similarity_search (k=3) over `data/docs/`. Backed by a lazily-opened, module-level singleton `_vs` in `doc_search.py`.
- `query_database` — SQLite read-only. Enforces SELECT-only via two checks: prefix must be `select`, and a `_FORBIDDEN` regex blocks `insert|update|delete|drop|alter|create|replace|attach|detach|pragma`. The schema is documented inside the tool's docstring so the LLM can author correct SQL.
- `search_web` — Tavily. Degrades gracefully if `TAVILY_API_KEY` is empty (returns an error string the LLM treats as "tool unavailable, try another").
- `calculate` — `numexpr.evaluate` (no `eval`). The system prompt explicitly tells Claude to never compute arithmetic in its head.

**Adding a new tool:** create `src/tools/foo.py` with a `@tool`-decorated function whose **docstring is the contract the LLM reads to decide when to call it**, then add it to `ALL_TOOLS` in `src/tools/__init__.py`. No other wiring is needed.

**Ingestion (`src/ingestion.py`):** `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)` with `["\n\n", "\n", "。", ".", " ", ""]` separators — the `。` separator is intentional for Chinese docs. Embeddings: `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace (~90 MB, downloaded on first run; set `HF_ENDPOINT=https://hf-mirror.com` if blocked). Only `.md` and `.txt` are loaded — adding PDF requires a new loader (e.g. `PyPDFLoader`) in `_load_docs`.

**Config (`config.py`):** loads `.env` via `python-dotenv` at import time. All paths (`CHROMA_PERSIST_DIR`, `SQLITE_PATH`, `DOCS_DIR`) are resolved relative to `rag_agent_demo/` regardless of CWD. `require_anthropic_key()` is the gate — `RagAgent` calls it lazily inside `_build_executor`, so importing modules without a key set won't crash.

## Conventions specific to this repo

- **Run from `rag_agent_demo/`**, not from a parent directory. `src.ingestion` and `src.tools.*` use absolute `src.*` imports; `tests/test_agent.py` injects the parent dir into `sys.path` itself, so `pytest` works from this directory.
- **Reply language**: the system prompt instructs the agent to reply in the user's language — preserve this when editing `SYSTEM_PROMPT`.
- **Verbose agent traces**: `AgentExecutor(verbose=True)` prints every tool call and intermediate step to stdout. This is intentional for the demo; don't silence it without reason.
- **Two CLAUDE.md files higher up the tree** (`~/CLAUDE.md` and `claude_code_sap_internal/CLAUDE.md`) define general behavioral guidelines (Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution). They apply here too.

## Reference

- `README.md` — feature overview, example questions showing tool routing.
- `RUNNING.md` — step-by-step run guide with expected outputs and a troubleshooting table (HF mirror, port-in-use, missing keys, etc.). Consult this before adding to "common errors".
