# tests/db/test_repo_sqlite.py
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from bs_pricer.db.models import (
    PricingInputs, PricingOutputs, PricingRun, RunId,
    SurfaceSpec, SurfaceData, SurfaceId, OptionType,
)
from bs_pricer.db.repo_sqlite import SQLiteRepo


def test_save_and_get_pricing_run(tmp_path: Path) -> None:
    repo = SQLiteRepo(tmp_path / "test.db")

    fixed = datetime(2026, 1, 30, tzinfo=timezone.utc)
    run = PricingRun(
        run_id=RunId("run-1"),
        inputs=PricingInputs(
            asof_utc=fixed, S=100, K=100, T=1, sigma=0.2, r=0.01, option_type=OptionType.CALL
        ),
        outputs=PricingOutputs(
            computed_at_utc=fixed, option_type=OptionType.CALL, price=10.0
        ),
    )

    repo.save_pricing_run(run)
    got = repo.get_pricing_run(RunId("run-1"))

    assert got == run


def test_save_and_get_surface(tmp_path: Path) -> None:
    repo = SQLiteRepo(tmp_path / "test.db")

    sid = SurfaceId("surf-1")
    fixed = datetime(2026, 1, 30, tzinfo=timezone.utc)

    spec = SurfaceSpec(
        surface_id=sid,
        created_at_utc=fixed,
        S_axis=(90, 100, 110),
        sigma_axis=(0.1, 0.2),
        K=100, T=1, r=0.01,
    )

    data = SurfaceData(
        surface_id=sid,
        computed_at_utc=fixed,
        call_matrix=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        put_matrix=[[6.0, 5.0, 4.0], [3.0, 2.0, 1.0]],
    )

    repo.save_surface(spec, data)
    got = repo.get_surface(sid)

    assert got is not None
    spec2, data2 = got
    assert spec2 == spec
    assert data2 == data