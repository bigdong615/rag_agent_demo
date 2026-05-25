"""Configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.resolve()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

CHROMA_PERSIST_DIR = str(ROOT / os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"))
SQLITE_PATH = str(ROOT / os.getenv("SQLITE_PATH", "./data/sample.db"))
DOCS_DIR = str(ROOT / os.getenv("DOCS_DIR", "./data/docs"))

CHROMA_COLLECTION = "rag_docs"


def require_anthropic_key() -> None:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
