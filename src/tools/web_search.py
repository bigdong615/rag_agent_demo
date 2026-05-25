"""Tool: web search via Tavily."""
from __future__ import annotations

from langchain_core.tools import tool

import config


@tool
def search_web(query: str) -> str:
    """Search the public web for up-to-date information.

    Use this when the user asks about news, recent events, current facts, or anything
    that is unlikely to be in the internal docs or database (e.g. competitor info,
    today's weather, today's stock price, latest releases).

    Args:
        query: A natural-language search query.

    Returns:
        Top-3 search results with title, snippet, and URL.
    """
    if not config.TAVILY_API_KEY:
        return "Error: TAVILY_API_KEY not configured. Web search is unavailable."

    try:
        from tavily import TavilyClient
    except ImportError:
        return "Error: tavily-python is not installed."

    try:
        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        resp = client.search(query=query, max_results=3, search_depth="basic")
    except Exception as e:
        return f"Web search error: {e}"

    results = resp.get("results", [])
    if not results:
        return "No web results found."

    parts = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        parts.append(f"[{i}] {title}\n{content}\nURL: {url}")
    return "\n\n---\n\n".join(parts)
