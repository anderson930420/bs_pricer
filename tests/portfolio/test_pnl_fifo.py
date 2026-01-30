from __future__ import annotations

from datetime import datetime, timezone

import pytest

from bs_pricer.portfolio.models import InstrumentId, Side, Trade
from bs_pricer.portfolio.pnl import InventoryError, apply_trades_fifo, unrealized_pnl_from_lots


def dt(y, m, d, hh=0, mm=0, ss=0):
    return datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc)


def test_fifo_realized_simple() -> None:
    inst = InstrumentId("AAPL")

    trades = [
        Trade(inst, dt(2026, 1, 1), Side.BUY, qty=1.0, price=100.0),
        Trade(inst, dt(2026, 1, 2), Side.SELL, qty=1.0, price=110.0),
    ]

    lots, rp = apply_trades_fifo(trades)
    assert lots == []
    assert rp.realized == 10.0
    assert rp.fees == 0.0


def test_fifo_realized_multi_lot_partial() -> None:
    inst = InstrumentId("AAPL")

    trades = [
        Trade(inst, dt(2026, 1, 1), Side.BUY, qty=1.0, price=100.0, fees=1.0),
        Trade(inst, dt(2026, 1, 2), Side.BUY, qty=1.0, price=105.0, fees=1.0),
        Trade(inst, dt(2026, 1, 3), Side.SELL, qty=1.5, price=110.0, fees=2.0),
    ]

    lots, rp = apply_trades_fifo(trades)

    # FIFO consumption:
    # sell 1.0 from cost 100 => +10
    # sell 0.5 from cost 105 => +2.5
    # gross realized = 12.5
    # fees total = 1+1+2 = 4
    # net realized = 8.5
    assert rp.fees == 4.0
    assert rp.realized == 8.5

    # remaining lot: 0.5 @ 105
    assert len(lots) == 1
    assert lots[0].qty == 0.5
    assert lots[0].cost_per_unit == 105.0


def test_fifo_sell_exceeds_inventory_raises() -> None:
    inst = InstrumentId("AAPL")
    trades = [
        Trade(inst, dt(2026, 1, 1), Side.BUY, qty=1.0, price=100.0),
        Trade(inst, dt(2026, 1, 2), Side.SELL, qty=1.1, price=110.0),
    ]

    with pytest.raises(InventoryError):
        apply_trades_fifo(trades)


def test_unrealized_from_lots() -> None:
    inst = InstrumentId("AAPL")
    trades = [
        Trade(inst, dt(2026, 1, 1), Side.BUY, qty=1.0, price=100.0),
        Trade(inst, dt(2026, 1, 2), Side.BUY, qty=2.0, price=110.0),
    ]
    lots, rp = apply_trades_fifo(trades)
    assert rp.realized == 0.0

    u = unrealized_pnl_from_lots(lots, mark_price=120.0)
    # (120-100)*1 + (120-110)*2 = 20 + 20 = 40
    assert u.unrealized == 40.0
