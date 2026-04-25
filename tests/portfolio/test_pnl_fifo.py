from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from bs_pricer.portfolio.models import InstrumentId, Side, Trade
from bs_pricer.portfolio import pnl as pnl_module
from bs_pricer.portfolio.pnl import InventoryError, QTY_EPSILON, apply_trades_fifo, unrealized_pnl_from_lots


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


def test_fifo_fractional_rounding_closes_position() -> None:
    inst = InstrumentId("AAPL")

    trades = [
        Trade(inst, dt(2026, 1, 1), Side.BUY, qty=0.1, price=100.0),
        Trade(inst, dt(2026, 1, 2), Side.BUY, qty=0.2, price=105.0),
        Trade(inst, dt(2026, 1, 3), Side.SELL, qty=0.3, price=110.0),
    ]

    lots, rp = apply_trades_fifo(trades)

    assert lots == []
    assert rp.fees == 0.0
    assert rp.realized == pytest.approx((110.0 - 100.0) * 0.1 + (110.0 - 105.0) * 0.2)


def test_fifo_preserves_nonzero_remaining_inventory() -> None:
    inst = InstrumentId("AAPL")

    trades = [
        Trade(inst, dt(2026, 1, 1), Side.BUY, qty=1.0, price=100.0),
        Trade(inst, dt(2026, 1, 2), Side.BUY, qty=2.0, price=110.0),
        Trade(inst, dt(2026, 1, 3), Side.SELL, qty=2.5, price=120.0),
    ]

    lots, rp = apply_trades_fifo(trades)

    assert len(lots) == 1
    assert lots[0].qty == 0.5
    assert lots[0].cost_per_unit == 110.0
    assert rp.realized == pytest.approx((120.0 - 100.0) * 1.0 + (120.0 - 110.0) * 1.5)


def test_fifo_uses_named_qty_epsilon_constant() -> None:
    source = Path(pnl_module.__file__).read_text()
    tree = ast.parse(source)

    assigned = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "QTY_EPSILON" for target in node.targets)
    ]
    assert len(assigned) == 1
    assert isinstance(assigned[0].value, ast.Constant)
    assert assigned[0].value.value == QTY_EPSILON

    assert "while remaining > 0" not in source
    assert "new_qty == 0" not in source
    assert "QTY_EPSILON" in source


def test_fifo_tolerance_is_applied_via_named_constant(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pnl_module, "QTY_EPSILON", 0.25)

    inst = InstrumentId("AAPL")
    trades = [
        Trade(inst, dt(2026, 1, 1), Side.BUY, qty=1.0, price=100.0),
        Trade(inst, dt(2026, 1, 2), Side.SELL, qty=0.9, price=110.0),
    ]

    lots, _ = apply_trades_fifo(trades)

    assert lots == []


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
