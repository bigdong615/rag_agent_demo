"""Smoke tests for individual tools (no LLM required).

Run: pytest tests/   (from rag_agent_demo/)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data import init_db  # noqa: E402
from src.tools.calculator import calculate  # noqa: E402
from src.tools.sql_query import query_database  # noqa: E402


def setup_module(_):
    init_db.init()


def test_calculator_basic():
    result = calculate.invoke({"expression": "1 + 2 * 3"})
    assert result == "7"


def test_calculator_invalid():
    result = calculate.invoke({"expression": "totally not math"})
    assert result.startswith("Calculator error")


def test_sql_select_employees():
    result = query_database.invoke(
        {"sql": "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 1"}
    )
    assert "王芳" in result
    assert "32000" in result


def test_sql_rejects_writes():
    result = query_database.invoke({"sql": "DELETE FROM employees"})
    assert result.startswith("Error")


def test_sql_rejects_forbidden_keyword():
    result = query_database.invoke(
        {"sql": "SELECT * FROM employees; DROP TABLE employees"}
    )
    assert "Error" in result or "forbidden" in result.lower()
