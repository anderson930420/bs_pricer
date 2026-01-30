from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .models import InstrumentId, Lot, RealizedPnL, Side, Trade, UnrealizedPnL


class InventoryError(ValueError):
    """Raised when sells exceed available inventory under FIFO policy."""


def apply_trades_fifo(trades: Iterable[Trade]) -> tuple[list[Lot], RealizedPnL]:
    """
    Apply trades under FIFO inventory accounting.
    Returns (open_lots, realized_pnl).

    Conventions:
      - BUY increases inventory, creates a new FIFO lot at trade.price.
      - SELL decreases inventory, consumes lots oldest-first.
      - Fees always subtract from realized PnL (both BUY and SELL fees).
    """
    trades_list = list(trades)
    if not trades_list:
        raise ValueError("trades is empty")

    inst: InstrumentId = trades_list[0].instrument_id
    for t in trades_list:
        if t.instrument_id != inst:
            raise ValueError("apply_trades_fifo expects a single instrument_id")
        if t.qty <= 0:
            raise ValueError("trade.qty must be > 0")
        if t.price < 0:
            raise ValueError("trade.price must be >= 0")
        if t.fees < 0:
            raise ValueError("trade.fees must be >= 0")

    lots: List[Lot] = []
    realized = 0.0
    fees_total = 0.0

    for t in trades_list:
        fees_total += t.fees

        if t.side == Side.BUY:
            lots.append(
                Lot(
                    instrument_id=t.instrument_id,
                    ts_utc=t.ts_utc,
                    qty=t.qty,
                    cost_per_unit=t.price,
                    source_trade_id=t.trade_id,
                )
            )
            continue

        if t.side != Side.SELL:
            raise ValueError(f"Unknown side: {t.side}")

        remaining = t.qty
        while remaining > 0:
            if not lots:
                raise InventoryError("SELL exceeds available inventory under FIFO")

            head = lots[0]
            take = head.qty if head.qty <= remaining else remaining

            # realized contribution: (sell - cost) * qty
            realized += (t.price - head.cost_per_unit) * take

            new_qty = head.qty - take
            remaining -= take

            if new_qty == 0:
                lots.pop(0)
            else:
                lots[0] = Lot(
                    instrument_id=head.instrument_id,
                    ts_utc=head.ts_utc,
                    qty=new_qty,
                    cost_per_unit=head.cost_per_unit,
                    source_trade_id=head.source_trade_id,
                )

    # Fees reduce realized PnL
    realized_after_fees = realized - fees_total
    return lots, RealizedPnL(instrument_id=inst, realized=realized_after_fees, fees=fees_total)


def unrealized_pnl_from_lots(lots: Iterable[Lot], *, mark_price: float) -> UnrealizedPnL:
    lots_list = list(lots)
    if not lots_list:
        raise ValueError("lots is empty")
    inst = lots_list[0].instrument_id
    for lot in lots_list:
        if lot.instrument_id != inst:
            raise ValueError("unrealized_pnl_from_lots expects a single instrument_id")
        if lot.qty <= 0:
            raise ValueError("lot.qty must be > 0")
        if lot.cost_per_unit < 0:
            raise ValueError("lot.cost_per_unit must be >= 0")
    if mark_price < 0:
        raise ValueError("mark_price must be >= 0")

    u = 0.0
    for lot in lots_list:
        u += (mark_price - lot.cost_per_unit) * lot.qty

    return UnrealizedPnL(instrument_id=inst, unrealized=u, mark_price=mark_price)
