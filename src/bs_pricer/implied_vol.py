from __future__ import annotations

from dataclasses import dataclass
import math
import numbers
from typing import Literal

from .validation import price_checked

OptionSide = Literal["call", "put"]


@dataclass(frozen=True)
class ImpliedVolatilityResult:
    option_type: OptionSide
    implied_volatility: float
    market_price: float
    model_price: float
    price_error: float
    iterations: int
    lower_bound: float
    upper_bound: float


def _require_finite_real_number(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"{name} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} is not finite")
    return result


def _checked_option_type(option_type: str) -> OptionSide:
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")
    return option_type


def _model_price(option_type: OptionSide, *, S: float, K: float, T: float, r: float, sigma: float) -> float:
    return float(price_checked(S=S, K=K, sigma=sigma, T=T, r=r)[option_type])


def _result(
    *,
    option_type: OptionSide,
    implied_volatility: float,
    market_price: float,
    model_price: float,
    iterations: int,
    lower_bound: float,
    upper_bound: float,
) -> ImpliedVolatilityResult:
    return ImpliedVolatilityResult(
        option_type=option_type,
        implied_volatility=implied_volatility,
        market_price=market_price,
        model_price=model_price,
        price_error=model_price - market_price,
        iterations=iterations,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
    )


def solve_implied_volatility(
    *,
    option_type: OptionSide,
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    tolerance: float = 1e-8,
    max_iterations: int = 100,
    max_sigma: float = 5.0,
) -> ImpliedVolatilityResult:
    """Solve single-option Black-Scholes implied volatility by bisection."""
    option_type = _checked_option_type(option_type)
    market_price = _require_finite_real_number("market_price", market_price)
    tolerance = _require_finite_real_number("tolerance", tolerance)
    max_sigma = _require_finite_real_number("max_sigma", max_sigma)

    if isinstance(max_iterations, bool) or not isinstance(max_iterations, numbers.Integral):
        raise TypeError("max_iterations must be an integer")
    max_iterations = int(max_iterations)

    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    if max_sigma <= 0:
        raise ValueError("max_sigma must be positive")

    T = _require_finite_real_number("T", T)
    if T == 0:
        raise ValueError("implied volatility is undefined when T == 0")

    # Let the existing checked pricing path enforce S/K/T/r domain policy.
    lower_bound = _model_price(option_type, S=S, K=K, T=T, r=r, sigma=0.0)
    upper_bound = float(S) if option_type == "call" else float(K) * math.exp(-float(r) * T)

    if market_price < lower_bound - tolerance:
        raise ValueError(
            f"market_price must be at least the deterministic lower bound ({lower_bound})"
        )

    if math.isclose(market_price, lower_bound, rel_tol=0.0, abs_tol=tolerance):
        return _result(
            option_type=option_type,
            implied_volatility=0.0,
            market_price=market_price,
            model_price=lower_bound,
            iterations=0,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

    if market_price >= upper_bound or math.isclose(market_price, upper_bound, rel_tol=0.0, abs_tol=tolerance):
        raise ValueError(f"market_price must be below the no-arbitrage upper bound ({upper_bound})")

    high_price = _model_price(option_type, S=S, K=K, T=T, r=r, sigma=max_sigma)
    high_error = high_price - market_price
    if high_error < -tolerance:
        raise ValueError(f"market_price cannot be bracketed by max_sigma ({max_sigma})")
    if abs(high_error) <= tolerance:
        return _result(
            option_type=option_type,
            implied_volatility=max_sigma,
            market_price=market_price,
            model_price=high_price,
            iterations=0,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

    sigma_low = 0.0
    sigma_high = max_sigma
    best_sigma = sigma_high
    best_price = high_price

    for iteration in range(1, max_iterations + 1):
        sigma_mid = (sigma_low + sigma_high) / 2.0
        mid_price = _model_price(option_type, S=S, K=K, T=T, r=r, sigma=sigma_mid)
        error = mid_price - market_price

        best_sigma = sigma_mid
        best_price = mid_price

        if abs(error) <= tolerance:
            return _result(
                option_type=option_type,
                implied_volatility=sigma_mid,
                market_price=market_price,
                model_price=mid_price,
                iterations=iteration,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )

        if error < 0.0:
            sigma_low = sigma_mid
        else:
            sigma_high = sigma_mid

    final_error = best_price - market_price
    if abs(final_error) <= tolerance:
        return _result(
            option_type=option_type,
            implied_volatility=best_sigma,
            market_price=market_price,
            model_price=best_price,
            iterations=max_iterations,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

    raise ValueError("implied volatility solver did not converge within max_iterations")


__all__ = ["ImpliedVolatilityResult", "solve_implied_volatility"]
