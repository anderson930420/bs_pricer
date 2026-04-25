from __future__ import annotations

import math

import pytest

from bs_pricer.implied_vol import ImpliedVolatilityResult, solve_implied_volatility
from bs_pricer.validation import price_checked


def _market_price(option_type: str, *, sigma: float = 0.2, S: float = 100.0, K: float = 100.0, T: float = 1.0, r: float = 0.05) -> float:
    return float(price_checked(S=S, K=K, sigma=sigma, T=T, r=r)[option_type])


def test_call_price_generated_from_known_sigma_recovers_implied_volatility() -> None:
    market_price = _market_price("call", sigma=0.2)

    result = solve_implied_volatility(
        option_type="call",
        market_price=market_price,
        S=100.0,
        K=100.0,
        T=1.0,
        r=0.05,
    )

    assert isinstance(result, ImpliedVolatilityResult)
    assert result.implied_volatility == pytest.approx(0.2, abs=1e-6)
    assert result.model_price == pytest.approx(market_price, abs=1e-8)


def test_put_price_generated_from_known_sigma_recovers_implied_volatility() -> None:
    market_price = _market_price("put", sigma=0.2)

    result = solve_implied_volatility(
        option_type="put",
        market_price=market_price,
        S=100.0,
        K=100.0,
        T=1.0,
        r=0.05,
    )

    assert result.implied_volatility == pytest.approx(0.2, abs=1e-6)
    assert result.model_price == pytest.approx(market_price, abs=1e-8)


def test_deterministic_lower_bound_price_returns_zero_implied_volatility() -> None:
    market_price = _market_price("call", sigma=0.0, S=120.0, K=100.0)

    result = solve_implied_volatility(
        option_type="call",
        market_price=market_price,
        S=120.0,
        K=100.0,
        T=1.0,
        r=0.05,
    )

    assert result.implied_volatility == 0.0
    assert result.model_price == pytest.approx(market_price)
    assert result.price_error == pytest.approx(0.0)
    assert result.iterations == 0


def test_expiry_rejects_as_undefined() -> None:
    with pytest.raises(ValueError, match="undefined"):
        solve_implied_volatility(
            option_type="call",
            market_price=1.0,
            S=100.0,
            K=100.0,
            T=0.0,
            r=0.05,
        )


def test_market_price_below_lower_bound_rejects() -> None:
    lower_bound = _market_price("call", sigma=0.0, S=120.0, K=100.0)

    with pytest.raises(ValueError, match="lower bound"):
        solve_implied_volatility(
            option_type="call",
            market_price=lower_bound - 0.01,
            S=120.0,
            K=100.0,
            T=1.0,
            r=0.05,
        )


def test_call_market_price_greater_than_or_equal_to_spot_rejects() -> None:
    with pytest.raises(ValueError, match="upper bound"):
        solve_implied_volatility(
            option_type="call",
            market_price=100.0,
            S=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
        )


def test_put_market_price_greater_than_or_equal_to_discounted_strike_rejects() -> None:
    discounted_strike = 100.0 * math.exp(-0.05 * 1.0)

    with pytest.raises(ValueError, match="upper bound"):
        solve_implied_volatility(
            option_type="put",
            market_price=discounted_strike,
            S=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
        )


def test_returned_model_price_is_close_to_market_price_and_diagnostics_are_populated() -> None:
    market_price = _market_price("call", sigma=0.35)

    result = solve_implied_volatility(
        option_type="call",
        market_price=market_price,
        S=100.0,
        K=100.0,
        T=1.0,
        r=0.05,
    )

    assert result.option_type == "call"
    assert result.market_price == market_price
    assert result.model_price == pytest.approx(market_price, abs=1e-8)
    assert result.price_error == pytest.approx(result.model_price - market_price)
    assert result.iterations > 0
    assert result.lower_bound == pytest.approx(_market_price("call", sigma=0.0))
    assert result.upper_bound == pytest.approx(100.0)


def test_invalid_tolerance_rejects() -> None:
    with pytest.raises(ValueError, match="tolerance"):
        solve_implied_volatility(
            option_type="call",
            market_price=10.0,
            S=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            tolerance=0.0,
        )


def test_invalid_max_iterations_rejects() -> None:
    with pytest.raises(ValueError, match="max_iterations"):
        solve_implied_volatility(
            option_type="call",
            market_price=10.0,
            S=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            max_iterations=0,
        )


def test_invalid_max_sigma_rejects() -> None:
    with pytest.raises(ValueError, match="max_sigma"):
        solve_implied_volatility(
            option_type="call",
            market_price=10.0,
            S=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            max_sigma=0.0,
        )


def test_valid_deep_otm_case_inside_bounds_does_not_crash() -> None:
    market_price = _market_price("call", sigma=0.2, S=50.0, K=100.0, T=1.0, r=0.05)

    result = solve_implied_volatility(
        option_type="call",
        market_price=market_price,
        S=50.0,
        K=100.0,
        T=1.0,
        r=0.05,
    )

    assert result.implied_volatility == pytest.approx(0.2, abs=1e-5)
    assert result.model_price == pytest.approx(market_price, abs=1e-8)
