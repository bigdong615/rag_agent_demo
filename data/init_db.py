"""Initialize sample.db with example employees + sales tables.

Run: python -m data.init_db   (from rag_agent_demo/)
or:  python rag_agent_demo/data/init_db.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sample.db"


def init() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE employees (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL,
            dept    TEXT NOT NULL,
            salary  INTEGER NOT NULL
        );

        CREATE TABLE sales (
            id      INTEGER PRIMARY KEY,
            year    INTEGER NOT NULL,
            quarter INTEGER NOT NULL,
            revenue INTEGER NOT NULL
        );
        """
    )

    cur.executemany(
        "INSERT INTO employees(name, dept, salary) VALUES (?, ?, ?)",
        [
            ("张伟", "工程部", 28000),
            ("李娜", "销售部", 22000),
            ("王芳", "工程部", 32000),
            ("陈强", "市场部", 18000),
            ("刘敏", "销售部", 25000),
        ],
    )

    cur.executemany(
        "INSERT INTO sales(year, quarter, revenue) VALUES (?, ?, ?)",
        [
            (2024, 1, 1200000),
            (2024, 2, 1450000),
            (2024, 3, 1380000),
            (2024, 4, 1620000),
            (2025, 1, 1750000),
        ],
    )

    conn.commit()
    conn.close()
    print(f"Initialized {DB_PATH}")


if __name__ == "__main__":
    init()
