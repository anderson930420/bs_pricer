from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType, Optional

# Keep IDs opaque and stable
InstrumentId = NewType("InstrumentId", str)


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True, slots=True)
class Trade:
    """
    A fill-level trade event.
    qty > 0 always. side determines sign.
    price is in quote currency per unit (e.g., USD per share).
    fees are in quote currency (optional) and applied to PnL.
    """
    instrument_id: InstrumentId
    ts_utc: datetime
    side: Side
    qty: float
    price: float
    fees: float = 0.0
    venue: Optional[str] = None
    trade_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class Lot:
    """
    FIFO lot (open inventory).
    qty > 0. cost_per_unit excludes fees unless your accounting wants otherwise.
    """
    instrument_id: InstrumentId
    ts_utc: datetime
    qty: float
    cost_per_unit: float
    source_trade_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class RealizedPnL:
    instrument_id: InstrumentId
    realized: float
    fees: float


@dataclass(frozen=True, slots=True)
class UnrealizedPnL:
    instrument_id: InstrumentId
    unrealized: float
    mark_price: float
