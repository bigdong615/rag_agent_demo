"""Tool: safe arithmetic evaluation via numexpr."""
from __future__ import annotations

import numexpr
from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.

    Supports +, -, *, /, **, parentheses, and standard math functions
    (sin, cos, log, exp, sqrt, etc.). Variables are not allowed.

    Use this whenever you need to do arithmetic — never compute it in your head.

    Args:
        expression: A math expression, e.g. "1750000 * 1.15" or "sqrt(2) + 3**2".

    Returns:
        The numeric result as a string, or an error message.
    """
    try:
        result = numexpr.evaluate(expression).item()
    except Exception as e:
        return f"Calculator error: {e}"
    return str(result)
