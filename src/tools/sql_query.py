"""Tool: read-only SQL query over the sample SQLite database."""
from __future__ import annotations

import re
import sqlite3

from langchain_core.tools import tool

import config

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma)\b",
    re.IGNORECASE,
)


@tool
def query_database(sql: str) -> str:
    """Execute a read-only SELECT query against the company SQLite database.

    Use this when the user asks about employees, salaries, departments, or revenue.

    Available tables in the SQLite database:

      employees(id INTEGER, name TEXT, dept TEXT, salary INTEGER)
        - Employee directory. dept values: '工程部', '销售部', '市场部'.

      sales(id INTEGER, year INTEGER, quarter INTEGER, revenue INTEGER)
        - Quarterly revenue records. revenue is in CNY.

    Only SELECT statements are allowed. Any data-modifying statement will be rejected.

    Args:
        sql: A single SELECT SQL statement.

    Returns:
        Query result as text (column headers + rows), or an error message.
    """
    sql = sql.strip().rstrip(";")
    if not sql.lower().lstrip().startswith("select"):
        return "Error: only SELECT statements are allowed."
    if _FORBIDDEN.search(sql):
        return "Error: forbidden keyword detected; only read-only SELECT is allowed."

    try:
        conn = sqlite3.connect(config.SQLITE_PATH)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
    except sqlite3.Error as e:
        return f"SQL error: {e}"

    if not rows:
        return "Query executed. No rows returned."

    lines = [" | ".join(cols), "-" * 40]
    for row in rows:
        lines.append(" | ".join(str(x) for x in row))
    return "\n".join(lines)
