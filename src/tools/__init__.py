"""Aggregate all tools used by the agent."""
from src.tools.calculator import calculate
from src.tools.doc_search import search_documents
from src.tools.sql_query import query_database
from src.tools.web_search import search_web

ALL_TOOLS = [search_documents, query_database, search_web, calculate]

__all__ = [
    "ALL_TOOLS",
    "calculate",
    "search_documents",
    "query_database",
    "search_web",
]
