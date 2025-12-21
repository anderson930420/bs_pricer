import pytest
import math
from bs_pricer.pricing import _d1_d2, price
from bs_pricer.pricing import _norm_cdf

def test_price_does_not_handle_missing_args():
    with pytest.raises(TypeError):
        price(100, 100, 0.2, 1)  # Missing r argument

def test_price_returns_dict_with_call_put_keys():
    result = price(100, 100, 0.2, 1, 0.05)
    assert isinstance(result, dict)
    assert "call" in result
    assert "put" in result

def test_norm_cdf_basic_properties():
    # N(0) = 0.5
    assert abs(_norm_cdf(0.0) - 0.5) < 1e-12

    # symmetry: N(-x) = 1 - N(x)
    x = 1.3
    assert abs(_norm_cdf(-x) - (1.0 - _norm_cdf(x))) < 1e-12

def test_norm_cdf_extreme_values():
    # N(10) ~ 1.0
    assert abs(_norm_cdf(10.0) - 1.0) < 1e-12

    # N(-10) ~ 0.0
    assert abs(_norm_cdf(-10.0) - 0.0) < 1e-12

def test_d1_d2_are_finite():
    d1, d2 = _d1_d2(100.0, 100.0, 0.2, 1.0, 0.05)
    assert math.isfinite(d1)
    assert math.isfinite(d2)