from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from bs_pricer.db.models import OptionType
from bs_pricer.db.repo_sqlite import SQLiteRepo
from bs_pricer.service.pricing_service import PricingService


def test_replay_matches_persisted_price(tmp_path: Path) -> None:
    repo = SQLiteRepo(tmp_path / "test.db")
    svc = PricingService(repo=repo)

    fixed = datetime(2026, 1, 30, tzinfo=timezone.utc)

    run = svc.run_point(
        S=100,
        K=100,
        T=1,
        sigma=0.2,
        r=0.05,
        option_type=OptionType.CALL,
        asof_utc=fixed,
        tags=("replay-test",),
    )

    # Replay: recompute using stored inputs
    inputs = run.inputs
    out = svc.engine(
        S=inputs.S,
        K=inputs.K,
        sigma=inputs.sigma,
        T=inputs.T,
        r=inputs.r,
    )

    replay_price = out["call"]
    assert replay_price == run.outputs.price
