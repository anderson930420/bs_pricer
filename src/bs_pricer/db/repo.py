# src/bs_pricer/db/repo.py
from __future__ import annotations

import json
import sqlite3
from typing import Iterable, Optional, Protocol

from bs_pricer.db.models import (
    PricingRun, RunId,
    SurfaceSpec, SurfaceData, SurfaceId,
)

class Repo(Protocol):
    # ---- pricing runs ----
    def save_pricing_run(self, run: PricingRun) -> None: ...
    def get_pricing_run(self, run_id: RunId) -> Optional[PricingRun]: ...
    def list_pricing_runs(self, limit: int = 100) -> Iterable[RunId]: ...

    # ---- surfaces ----
    def save_surface(self, spec: SurfaceSpec, data: SurfaceData) -> None: ...
    def get_surface(self, surface_id: SurfaceId) -> Optional[tuple[SurfaceSpec, SurfaceData]]: ...