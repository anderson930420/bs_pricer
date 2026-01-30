from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bs_pricer.db.models import PricingRun, RunId
from bs_pricer.db.repo import Repo

from bs_pricer.portfolio.models import (
    InstrumentId,
    RealizedPnL,
    Trade,
    UnrealizedPnL,
)
from bs_pricer.portfolio.pnl import (
    apply_trades_fifo,
    unrealized_pnl_from_lots,
)


class MarkNotFoundError(LookupError):
    """Raised when the pricing run used as mark cannot be found."""


@dataclass(frozen=True, slots=True)
class PnLSummary:
    instrument_id: InstrumentId
    mark_run_id: RunId
    mark_price: float
    realized: RealizedPnL
    unrealized: UnrealizedPnL
    net: float


def _extract_mark_price(run: PricingRun) -> float:
    """
    Extract mark price from a persisted pricing run.

    Current schema stores exactly one option_type price per run,
    so this is unambiguous by design.
    """
    return float(run.outputs.price)


def compute_pnl_with_mark_run(
    *,
    repo: Repo,
    mark_run_id: RunId,
    trades: Iterable[Trade],
) -> PnLSummary:
    """
    Compute FIFO PnL using a persisted pricing run as the mark.

    Responsibilities:
      - Fetch pricing run from repo
      - Use its price as mark
      - Apply FIFO inventory accounting
      - Return a consolidated PnL summary

    This function does NOT:
      - Persist anything
      - Modify pricing schema
      - Perform pricing itself
    """
    run = repo.get_pricing_run(mark_run_id)
    if run is None:
        raise MarkNotFoundError(f"mark run not found: {mark_run_id}")

    mark_price = _extract_mark_price(run)

    open_lots, realized = apply_trades_fifo(trades)
    unrealized = unrealized_pnl_from_lots(open_lots, mark_price=mark_price)

    inst = realized.instrument_id
    net = realized.realized + unrealized.unrealized

    return PnLSummary(
        instrument_id=inst,
        mark_run_id=mark_run_id,
        mark_price=mark_price,
        realized=realized,
        unrealized=unrealized,
        net=net,
    )
