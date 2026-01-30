# src/bs_pricer/db/repo_sqlite.py
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from bs_pricer.db.models import (
    PricingRun, RunId,
    SurfaceSpec, SurfaceData, SurfaceId,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pricing_runs (
    run_id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS surfaces (
    surface_id TEXT PRIMARY KEY,
    spec_json TEXT NOT NULL,
    data_json TEXT NOT NULL
);
"""

class SQLiteRepo:
    def __init__(self, db_path: Path | str) -> None:
        self._path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path)

    def _init_db(self) -> None:
        with self._connect() as cx:
            cx.executescript(_SCHEMA)

    # -------- pricing runs --------
    def save_pricing_run(self, run: PricingRun) -> None:
        payload = json.dumps(run.to_record())
        with self._connect() as cx:
            cx.execute(
                "INSERT OR REPLACE INTO pricing_runs (run_id, payload_json) VALUES (?, ?)",
                (run.run_id, payload),
            )

    def get_pricing_run(self, run_id: RunId) -> Optional[PricingRun]:
        with self._connect() as cx:
            cur = cx.execute(
                "SELECT payload_json FROM pricing_runs WHERE run_id = ?",
                (run_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        rec = json.loads(row[0])
        return PricingRun.from_record(rec)

    def list_pricing_runs(self, limit: int = 100) -> Iterable[RunId]:
        with self._connect() as cx:
            cur = cx.execute(
                "SELECT run_id FROM pricing_runs ORDER BY rowid DESC LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()
        return (RunId(r[0]) for r in rows)

    # -------- surfaces --------
    def save_surface(self, spec: SurfaceSpec, data: SurfaceData) -> None:
        with self._connect() as cx:
            cx.execute(
                "INSERT OR REPLACE INTO surfaces (surface_id, spec_json, data_json) VALUES (?, ?, ?)",
                (
                    data.surface_id,
                    json.dumps(spec.to_record()),
                    json.dumps(data.to_record()),
                ),
            )

    def get_surface(self, surface_id: SurfaceId) -> Optional[tuple[SurfaceSpec, SurfaceData]]:
        with self._connect() as cx:
            cur = cx.execute(
                "SELECT spec_json, data_json FROM surfaces WHERE surface_id = ?",
                (surface_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        spec = SurfaceSpec.from_record(json.loads(row[0]))
        data = SurfaceData.from_record(json.loads(row[1]))
        return spec, data