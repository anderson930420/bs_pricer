from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from bs_pricer.db.models import OptionType
from bs_pricer.db.repo_sqlite import SQLiteRepo
from bs_pricer.service.pricing_service import PricingService


def test_run_point_persists(tmp_path: Path) -> None:
    repo = SQLiteRepo(tmp_path / "test.db")

    def fake_engine(**kwargs) -> dict:
        return {"call": 123.45, "put": 67.89}

    svc = PricingService(repo=repo, engine=fake_engine)

    fixed = datetime(2026, 1, 30, tzinfo=timezone.utc)
    run = svc.run_point(
        S=100, K=100, T=1, sigma=0.2, r=0.01,
        option_type=OptionType.CALL,
        asof_utc=fixed,
        tags=("svc",),
    )

    got = repo.get_pricing_run(run.run_id)
    assert got == run
    assert got.outputs.price == 123.45
