from __future__ import annotations

import sqlite3
from pathlib import Path

from bs_pricer.db.repo_sqlite import SQLiteRepo


def test_repo_initializes_schema(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    _ = SQLiteRepo(db)

    cx = sqlite3.connect(str(db))
    try:
        tables = {
            r[0]
            for r in cx.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        cx.close()

    # These are your contract tables (adjust if your names differ)
    assert "pricing_runs" in tables
    assert "surfaces" in tables
