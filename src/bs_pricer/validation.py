from __future__ import annotations

import math
import numbers

from . import pricing
from . import greeks as greeks_module


def _is_finite_real_number(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if not isinstance(value, numbers.Real):
        return False
    return math.isfinite(float(value))


def _require_finite_real_number(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"{name} must be a number")
    if not _is_finite_real_number(value):
        raise ValueError(f"{name} is not finite")


def _validate_numbers(S, K, sigma, T, r):
    # 檢查 type + NaN/inf（重點：NaN/inf）
    _require_finite_real_number("S", S)
    _require_finite_real_number("K", K)
    _require_finite_real_number("sigma", sigma)
    _require_finite_real_number("T", T)
    _require_finite_real_number("r", r)

def _validate_domain(S, K, sigma, T, r):
    # S > 0, K > 0
    # T >= 0, sigma >= 0
    # r 不限制正負
    if  S <= 0:
        raise ValueError("S must > 0")
    if not K > 0:
        raise ValueError("K must > 0")
    if not sigma >= 0:
        raise ValueError("sigma must be non-negative")
    if not T >= 0:
        raise ValueError("T must be non-negative")

def _payoff_at_expiry(S, K):
    # 回 {"call": ..., "put": ...}
    call_price = max(0.0, S - K)
    put_price = max(0.0, K - S)
    return {"call": call_price, "put": put_price}

def _deterministic_limit_sigma_zero(S, K, T, r):
    # σ=0, T>0 的 policy
    # 回 {"call": ..., "put": ...}
    pv_k = K * math.exp(-r*T)
    expected_call = max(S - pv_k, 0)
    expected_put = max(pv_k - S, 0)
    return {"call": expected_call, "put": expected_put}

def price_checked(S, K, sigma, T, r):
    _validate_numbers(S, K, sigma, T, r)
    _validate_domain(S, K, sigma, T, r)

    if T == 0:
        return _payoff_at_expiry(S, K)

    elif sigma == 0:
        return _deterministic_limit_sigma_zero(S, K, T, r)

    # normal path
    return pricing.price(S, K, sigma, T, r)


def greeks_checked(S, K, sigma, T, r):
    """Validate inputs and return analytic Black-Scholes Greeks.

    Analytic Greeks are only available for T > 0 and sigma > 0. Pricing still
    supports T == 0 and sigma == 0 via deterministic policies.
    """
    _validate_numbers(S, K, sigma, T, r)
    _validate_domain(S, K, sigma, T, r)

    if T == 0:
        raise ValueError("analytic Greeks are unavailable when T == 0")
    if sigma == 0:
        raise ValueError("analytic Greeks are unavailable when sigma == 0")

    return greeks_module.greeks(S, K, sigma, T, r)
