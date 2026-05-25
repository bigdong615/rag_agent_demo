"""Tool: semantic search over local document vectorstore."""
from __future__ import annotations

from langchain_core.tools import tool

from src.ingestion import get_vectorstore

_vs = None


def _store():
    global _vs
    if _vs is None:
        _vs = get_vectorstore()
    return _vs


@tool
def search_documents(query: str) -> str:
    """Search the internal product documentation (RockBot product intro, FAQ, etc.).

    Use this when the user asks about RockBot product features, pricing, deployment,
    SLA, FAQ, or any internal company knowledge.

    Args:
        query: A natural-language search query in any language.

    Returns:
        Top-3 relevant document snippets with their source filenames.
    """
    docs = _store().similarity_search(query, k=3)
    if not docs:
        return "No relevant documents found."

    parts = []
    for i, d in enumerate(docs, 1):
        source = d.metadata.get("source", "unknown")
        parts.append(f"[{i}] (source: {source})\n{d.page_content}")
    return "\n\n---\n\n".join(parts)
