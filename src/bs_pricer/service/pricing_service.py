from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from uuid import uuid4

from bs_pricer.db.models import (
    PricingInputs,
    PricingOutputs,
    PricingRun,
    RunId,
    SurfaceSpec,
    SurfaceData,
    SurfaceId,
    OptionType,
)
from bs_pricer.db.repo import Repo
from bs_pricer.surface import value_surface, ValueSurface
from bs_pricer.validation import price_checked


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


PriceEngine = Callable[..., Any]


def _extract_price(out: Any, option_type: OptionType) -> float:
    """
    Adapter: current engine returns {'call': float, 'put': float}.
    Keep this logic here so service public contract stays stable.
    """
    if not isinstance(out, dict):
        raise TypeError("Engine output must be a dict like {'call': float, 'put': float}")
    key = "call" if option_type == OptionType.CALL else "put"
    return float(out[key])


def _to_matrix(x: Any) -> list[list[float]]:
    # Storage contract: JSON-friendly nested lists
    if hasattr(x, "tolist"):
        return x.tolist()
    return [list(row) for row in x]


@dataclass(frozen=True, slots=True)
class PricingService:
    repo: Repo
    engine: PriceEngine = price_checked

    def run_point(
        self,
        *,
        S: float,
        K: float,
        T: float,
        sigma: float,
        r: float,
        option_type: OptionType,
        run_id: Optional[RunId] = None,
        asof_utc: Optional[datetime] = None,
        tags: tuple[str, ...] = (),
        notes: Optional[str] = None,
        instrument_id: Optional[str] = None,
    ) -> PricingRun:
        rid = run_id or RunId(str(uuid4()))
        asof = asof_utc or utc_now()

        inputs = PricingInputs(
            run_id=rid,
            instrument_id=instrument_id,
            asof_utc=asof,
            S=S,
            K=K,
            T=T,
            sigma=sigma,
            r=r,
            option_type=option_type,
            tags=tags,
            notes=notes,
        )

        out = self.engine(S=S, K=K, sigma=sigma, T=T, r=r)
        price = _extract_price(out, option_type)

        outputs = PricingOutputs(
            run_id=rid,
            computed_at_utc=utc_now(),
            option_type=option_type,
            price=price,
            engine=getattr(self.engine, "__name__", None),
        )

        run = PricingRun(run_id=rid, inputs=inputs, outputs=outputs)
        self.repo.save_pricing_run(run)
        return run

    def run_surface(
        self,
        *,
        S_axis: tuple[float, ...],
        sigma_axis: tuple[float, ...],
        K: float,
        T: float,
        r: float,
        surface_id: Optional[SurfaceId] = None,
        created_at_utc: Optional[datetime] = None,
        tags: tuple[str, ...] = (),
        notes: Optional[str] = None,
        engine: PriceEngine = price_checked,
    ) -> tuple[SurfaceSpec, SurfaceData]:
        sid = surface_id or SurfaceId(str(uuid4()))
        created = created_at_utc or utc_now()

        spec = SurfaceSpec(
            surface_id=sid,
            created_at_utc=created,
            S_axis=S_axis,
            sigma_axis=sigma_axis,
            K=K,
            T=T,
            r=r,
            engine=getattr(engine, "__name__", None),
            tags=tags,
            notes=notes,
        )

        vs: ValueSurface = value_surface(
            S_axis=S_axis,
            sigma_axis=sigma_axis,
            K=K,
            T=T,
            r=r,
            engine=engine,
        )

        # Prefer your ValueSurface contract first; fallback to common alt names.
        call_mat = getattr(vs, "call_matrix", None)
        put_mat = getattr(vs, "put_matrix", None)
        if call_mat is None or put_mat is None:
            call_mat = getattr(vs, "call", None)
            put_mat = getattr(vs, "put", None)
        if call_mat is None or put_mat is None:
            raise AttributeError("ValueSurface must expose call_matrix/put_matrix (or call/put)")

        data = SurfaceData(
            surface_id=sid,
            computed_at_utc=utc_now(),
            call_matrix=_to_matrix(call_mat),
            put_matrix=_to_matrix(put_mat),
            engine_version=None,
        )

        self.repo.save_surface(spec, data)
        return spec, data
