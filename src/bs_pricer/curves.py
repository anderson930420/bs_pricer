from __future__ import annotations

from dataclasses import dataclass
import math
import numbers
from typing import Literal

import numpy as np

from .validation import price_checked

OptionType = Literal["call", "put"]


@dataclass(frozen=True, slots=True)
class CurvePoint:
    spot: float
    payoff: float
    value: float
    intrinsic: float
    time_value: float


@dataclass(frozen=True, slots=True)
class PayoffValueCurve:
    option_type: OptionType
    points: tuple[CurvePoint, ...]


def _require_finite_real(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"{name} must be a number")
    as_float = float(value)
    if not math.isfinite(as_float):
        raise ValueError(f"{name} is not finite")
    return as_float


def _validate_option_type(option_type: str) -> OptionType:
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")
    return option_type


def _spot_axis(*, spot_min: float, spot_max: float, points: int) -> tuple[float, ...]:
    if isinstance(points, bool) or not isinstance(points, int):
        raise TypeError("points must be an integer")
    if points < 2:
        raise ValueError("points must be >= 2")

    lo = _require_finite_real("spot_min", spot_min)
    hi = _require_finite_real("spot_max", spot_max)

    if lo <= 0:
        raise ValueError("spot_min must be > 0")
    if hi <= lo:
        raise ValueError("spot_max must be > spot_min")

    return tuple(np.linspace(lo, hi, points, dtype=float).tolist())


def _side_intrinsic(*, option_type: OptionType, S: float, K: float) -> float:
    if option_type == "call":
        return max(S - K, 0.0)
    return max(K - S, 0.0)


def build_payoff_value_curve(
    *,
    option_type: OptionType,
    K: float,
    T: float,
    r: float,
    sigma: float,
    spot_min: float,
    spot_max: float,
    points: int,
) -> PayoffValueCurve:
    """Build selected-option payoff and value curve data over a spot axis."""

    selected_option = _validate_option_type(option_type)
    axis = _spot_axis(spot_min=spot_min, spot_max=spot_max, points=points)

    rows: list[CurvePoint] = []
    for spot in axis:
        prices = price_checked(S=spot, K=K, sigma=sigma, T=T, r=r)
        value = float(prices[selected_option])
        intrinsic = _side_intrinsic(option_type=selected_option, S=spot, K=K)
        rows.append(
            CurvePoint(
                spot=spot,
                payoff=intrinsic,
                value=value,
                intrinsic=intrinsic,
                time_value=value - intrinsic,
            )
        )

    return PayoffValueCurve(option_type=selected_option, points=tuple(rows))
