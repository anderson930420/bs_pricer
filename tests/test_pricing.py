import pytest
import math
import inspect
import sys
from bs_pricer.pricing import _d1_d2, price
from bs_pricer.pricing import _norm_cdf
from bs_pricer import _bs_core

def test_price_does_not_handle_missing_args():
    with pytest.raises(TypeError):
        price(100, 100, 0.2, 1)  # Missing r argument

def test_price_returns_dict_with_call_put_keys():
    result = price(100, 100, 0.2, 1, 0.05)
    assert isinstance(result, dict)
    assert "call" in result
    assert "put" in result
    assert math.isfinite(result["call"])
    assert math.isfinite(result["put"])

def test_norm_cdf_monotonic():
    x = [-10.0, -5.0, 0.0, 5.0, 10.0]
    y = [_norm_cdf(val) for val in x]
    assert y == sorted(y)

def test_norm_cdf_symmetry():
    xs = [0.1, 0.5, 1.0, 2.0, 3.0]
    tol = 1e-5
    for x in xs:
        lhs = _norm_cdf(-x)
        rhs = 1.0 - _norm_cdf(x)
        diff = abs(lhs - rhs)
        assert diff < tol

def test_norm_cdf_extreme_values_are_near_bounds(): 
    assert _norm_cdf(10.0) > 0.999
    assert _norm_cdf(-10.0) < 0.001 

def test_norm_cdf_range():
    x = [-10.0, -5.0, 0.0, 5.0, 10.0]
    y = [_norm_cdf(val) for val in x]
    assert all(0 <= val <= 1 for val in y)

def test_d1_d2_are_finite():
    d1, d2 = _d1_d2(100.0, 100.0, 0.2, 1.0, 0.05)
    assert math.isfinite(d1)
    assert math.isfinite(d2)

def test_price_non_negative():
    result = price(100, 100, 0.2, 1, 0.05)
    assert result["call"] >= -1e-12
    assert result["put"] >= -1e-12


def test_norm_pdf_zero_matches_standard_normal_constant():
    assert _bs_core.norm_pdf(0.0) == pytest.approx(1.0 / math.sqrt(2.0 * math.pi))


def test_core_norm_cdf_zero_is_half():
    assert _bs_core.norm_cdf(0.0) == pytest.approx(0.5)


def test_pricing_behavior_remains_unchanged_after_core_refactor():
    result = price(100.0, 100.0, 0.2, 1.0, 0.05)
    assert result["call"] == pytest.approx(10.450583572185565)
    assert result["put"] == pytest.approx(5.573526022256971)


def test_scalar_core_does_not_import_numpy():
    source = inspect.getsource(_bs_core)
    assert "import numpy" not in source
    assert "numpy" not in sys.modules or _bs_core.__name__ != "numpy"
