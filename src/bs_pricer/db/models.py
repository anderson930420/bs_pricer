# src/bs_pricer/db/models.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Mapping, NewType, Optional, Sequence

# -----------------------------
# Schema versioning (module-level contract)
# -----------------------------

SCHEMA_VERSION: int = 1


def utc_now() -> datetime:
    # models can create timestamps, but do not touch IO / persistence
    return datetime.now(timezone.utc)


def _require_utc(dt: datetime) -> datetime:
    # structural contract only: timestamps must be timezone-aware UTC
    # (domain validation of finance params stays elsewhere)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)


# -----------------------------
# Strongly-typed identifiers (repo decides actual storage shape)
# -----------------------------

RunId = NewType("RunId", str)          # typically UUID string
InstrumentId = NewType("InstrumentId", str)
SurfaceId = NewType("SurfaceId", str)


class OptionType(str, Enum):
    CALL = "C"
    PUT = "P"


# -----------------------------
# Core domain-ish models (pure schema, no pricing logic)
# -----------------------------

@dataclass(frozen=True, slots=True, kw_only=True)
class PricingInputs:
    """
    Schema for one Black–Scholes pricing request.
    NOTE: No domain checks here (S>0, K>0, etc.). Those live in validation.py / engine.
    """
    schema_version: int = SCHEMA_VERSION

    # Identity / linkage (optional; repo/service can populate)
    run_id: Optional[RunId] = None
    instrument_id: Optional[InstrumentId] = None

    # As-of timestamp for this computation (UTC)
    asof_utc: datetime = utc_now()

    # Parameters (match pricing.py signature style)
    S: float = 0.0
    K: float = 0.0
    T: float = 0.0
    sigma: float = 0.0
    r: float = 0.0
    option_type: OptionType = OptionType.CALL

    # Free-form metadata (kept JSON-friendly)
    tags: tuple[str, ...] = ()
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "asof_utc", _require_utc(self.asof_utc))

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "instrument_id": self.instrument_id,
            "asof_utc": self.asof_utc.isoformat(),
            "S": self.S,
            "K": self.K,
            "T": self.T,
            "sigma": self.sigma,
            "r": self.r,
            "option_type": self.option_type.value,
            "tags": list(self.tags),
            "notes": self.notes,
        }

    @classmethod
    def from_record(cls, rec: Mapping[str, Any]) -> "PricingInputs":
        return cls(
            schema_version=int(rec.get("schema_version", SCHEMA_VERSION)),
            run_id=rec.get("run_id"),
            instrument_id=rec.get("instrument_id"),
            asof_utc=_require_utc(datetime.fromisoformat(rec["asof_utc"])),
            S=float(rec["S"]),
            K=float(rec["K"]),
            T=float(rec["T"]),
            sigma=float(rec["sigma"]),
            r=float(rec["r"]),
            option_type=OptionType(rec["option_type"]),
            tags=tuple(rec.get("tags", ())),
            notes=rec.get("notes"),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PricingOutputs:
    """
    Schema for pricing result.
    Keep minimal + stable: store only what downstream needs.
    If you later want greeks, add fields with defaults (schema_version bump if breaking).
    """
    schema_version: int = SCHEMA_VERSION

    run_id: Optional[RunId] = None
    computed_at_utc: datetime = utc_now()

    option_type: OptionType = OptionType.CALL
    price: float = 0.0

    # Useful for audit/debug, but optional (do not force core to compute)
    d1: Optional[float] = None
    d2: Optional[float] = None

    # Engine bookkeeping (repo/service can fill)
    engine: Optional[str] = None          # e.g. "price_checked"
    engine_version: Optional[str] = None  # e.g. package version / git sha

    def __post_init__(self) -> None:
        object.__setattr__(self, "computed_at_utc", _require_utc(self.computed_at_utc))

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "computed_at_utc": self.computed_at_utc.isoformat(),
            "option_type": self.option_type.value,
            "price": self.price,
            "d1": self.d1,
            "d2": self.d2,
            "engine": self.engine,
            "engine_version": self.engine_version,
        }

    @classmethod
    def from_record(cls, rec: Mapping[str, Any]) -> "PricingOutputs":
        return cls(
            schema_version=int(rec.get("schema_version", SCHEMA_VERSION)),
            run_id=rec.get("run_id"),
            computed_at_utc=_require_utc(datetime.fromisoformat(rec["computed_at_utc"])),
            option_type=OptionType(rec["option_type"]),
            price=float(rec["price"]),
            d1=rec.get("d1"),
            d2=rec.get("d2"),
            engine=rec.get("engine"),
            engine_version=rec.get("engine_version"),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PricingRun:
    """
    One atomic computation run = inputs + outputs.
    Repo may store normalized tables, but public contract can expose this aggregate.
    """
    schema_version: int = SCHEMA_VERSION
    run_id: RunId

    inputs: PricingInputs
    outputs: PricingOutputs

    def to_record(self) -> dict[str, Any]:
        # aggregate record; repo can also split into 2 tables if desired
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "inputs": self.inputs.to_record(),
            "outputs": self.outputs.to_record(),
        }

    @classmethod
    def from_record(cls, rec: Mapping[str, Any]) -> "PricingRun":
        return cls(
            schema_version=int(rec.get("schema_version", SCHEMA_VERSION)),
            run_id=RunId(rec["run_id"]),
            inputs=PricingInputs.from_record(rec["inputs"]),
            outputs=PricingOutputs.from_record(rec["outputs"]),
        )


# -----------------------------
# Surface models (grid spec + computed matrices)
# -----------------------------

@dataclass(frozen=True, slots=True, kw_only=True)
class SurfaceSpec:
    """
    Defines a surface job request (grid axes + pricing constants).
    Axis contract/shape contract stays in surface layer; here we only store data.
    """
    schema_version: int = SCHEMA_VERSION

    surface_id: Optional[SurfaceId] = None
    created_at_utc: datetime = utc_now()

    # axes: store as tuples for immutability; repo serializes as JSON arrays
    S_axis: tuple[float, ...] = ()
    sigma_axis: tuple[float, ...] = ()

    # constants shared across surface computation
    K: float = 0.0
    T: float = 0.0
    r: float = 0.0

    engine: Optional[str] = None
    tags: tuple[str, ...] = ()
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at_utc", _require_utc(self.created_at_utc))

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "surface_id": self.surface_id,
            "created_at_utc": self.created_at_utc.isoformat(),
            "S_axis": list(self.S_axis),
            "sigma_axis": list(self.sigma_axis),
            "K": self.K,
            "T": self.T,
            "r": self.r,
            "engine": self.engine,
            "tags": list(self.tags),
            "notes": self.notes,
        }

    @classmethod
    def from_record(cls, rec: Mapping[str, Any]) -> "SurfaceSpec":
        return cls(
            schema_version=int(rec.get("schema_version", SCHEMA_VERSION)),
            surface_id=rec.get("surface_id"),
            created_at_utc=_require_utc(datetime.fromisoformat(rec["created_at_utc"])),
            S_axis=tuple(rec.get("S_axis", ())),
            sigma_axis=tuple(rec.get("sigma_axis", ())),
            K=float(rec["K"]),
            T=float(rec["T"]),
            r=float(rec["r"]),
            engine=rec.get("engine"),
            tags=tuple(rec.get("tags", ())),
            notes=rec.get("notes"),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SurfaceData:
    """
    Computed result payload.
    Matrices are stored as JSON-friendly nested lists (repo may choose flattening).
    """
    schema_version: int = SCHEMA_VERSION

    surface_id: SurfaceId
    computed_at_utc: datetime = utc_now()

    # In ValueSurface you already have call/put matrices; store both.
    call_matrix: Sequence[Sequence[float]] = ()
    put_matrix: Sequence[Sequence[float]] = ()

    engine_version: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "computed_at_utc", _require_utc(self.computed_at_utc))

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "surface_id": self.surface_id,
            "computed_at_utc": self.computed_at_utc.isoformat(),
            "call_matrix": self.call_matrix,
            "put_matrix": self.put_matrix,
            "engine_version": self.engine_version,
        }

    @classmethod
    def from_record(cls, rec: Mapping[str, Any]) -> "SurfaceData":
        return cls(
            schema_version=int(rec.get("schema_version", SCHEMA_VERSION)),
            surface_id=SurfaceId(rec["surface_id"]),
            computed_at_utc=_require_utc(datetime.fromisoformat(rec["computed_at_utc"])),
            call_matrix=rec["call_matrix"],
            put_matrix=rec["put_matrix"],
            engine_version=rec.get("engine_version"),
        )


__all__ = [
    "SCHEMA_VERSION",
    "RunId",
    "InstrumentId",
    "SurfaceId",
    "OptionType",
    "PricingInputs",
    "PricingOutputs",
    "PricingRun",
    "SurfaceSpec",
    "SurfaceData",
]
