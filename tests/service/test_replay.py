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

    # Persist one run (CALL)
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

    # Load it back (ensures read-side works too)
    run_db = repo.get_pricing_run(run.run_id)
    assert run_db is not None
    assert run_db == run

    # Replay: recompute from persisted inputs using the same engine contract
    inp = run_db.inputs
    out = svc.engine(S=inp.S, K=inp.K, sigma=inp.sigma, T=inp.T, r=inp.r)

    # Compare the same option_type price
    if run_db.outputs.option_type == OptionType.CALL:
        replay_price = float(out["call"])
    else:
        replay_price = float(out["put"])

    assert replay_price == run_db.outputs.price
