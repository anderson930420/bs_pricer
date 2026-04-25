import pytest

from bs_pricer.greeks import Greeks, GreekValues, greeks
from bs_pricer.validation import greeks_checked, price_checked


def test_greeks_data_model_access_style():
    values = greeks(100.0, 100.0, 0.2, 1.0, 0.05)

    assert isinstance(values, Greeks)
    assert isinstance(values.call, GreekValues)
    assert isinstance(values.put, GreekValues)
    assert isinstance(values.call.delta, float)
    assert isinstance(values.put.theta, float)


def test_greek_signs_and_call_put_symmetry_under_standard_conditions():
    values = greeks_checked(100.0, 100.0, 0.2, 1.0, 0.05)

    assert values.call.delta > 0
    assert values.put.delta < 0
    assert values.call.gamma > 0
    assert values.call.gamma == pytest.approx(values.put.gamma)
    assert values.call.vega == pytest.approx(values.put.vega)
    assert values.call.theta < 0
    assert values.put.theta < 0
    assert values.call.rho > 0
    assert values.put.rho < 0


def test_checked_greeks_reject_t_zero_without_blocking_pricing():
    with pytest.raises(ValueError, match="T == 0"):
        greeks_checked(100.0, 100.0, 0.2, 0.0, 0.05)

    prices = price_checked(100.0, 100.0, 0.2, 0.0, 0.05)
    assert prices == {"call": 0.0, "put": 0.0}


def test_checked_greeks_reject_sigma_zero_without_blocking_pricing():
    with pytest.raises(ValueError, match="sigma == 0"):
        greeks_checked(100.0, 100.0, 0.0, 1.0, 0.05)

    prices = price_checked(100.0, 100.0, 0.0, 1.0, 0.05)
    assert prices["call"] > 0
    assert prices["put"] == pytest.approx(0.0)
