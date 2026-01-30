import pytest
from bs_pricer.portfolio.models import InstrumentId, Side, Trade
from datetime import datetime, timezone

def dt(y,m,d):
    return datetime(y,m,d,tzinfo=timezone.utc)

def test_service_rejects_mixed_instruments(tmp_path):
    from bs_pricer.db.repo_sqlite import SQLiteRepo
    from bs_pricer.service.pricing_service import PricingService
    from bs_pricer.db.models import OptionType
    from bs_pricer.portfolio.service import compute_pnl_with_mark_run

    repo = SQLiteRepo(tmp_path / "test.db")
    pricing = PricingService(repo=repo)
    run = pricing.run_point(S=100, K=100, T=1, sigma=0.2, r=0.05, option_type=OptionType.CALL)

    t1 = Trade(InstrumentId("AAPL"), dt(2026,1,1), Side.BUY, 1.0, 90.0)
    t2 = Trade(InstrumentId("MSFT"), dt(2026,1,2), Side.BUY, 1.0, 95.0)

    with pytest.raises(ValueError):
        compute_pnl_with_mark_run(repo=repo, mark_run_id=run.run_id, trades=[t1, t2])
