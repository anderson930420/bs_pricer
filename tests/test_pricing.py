from unittest import result
import pytest
import math
from bs_pricer.pricing import price
from bs_pricer.pricing import _norm_cdf
def test_price_not_implemented():
    with pytest.raises(NotImplementedError):
        price(100, 100, 0.2, 1, 0.05)

def test_price_does_not_handle_missing_args():
    with pytest.raises(TypeError):
        price(100, 100, 0.2, 1)  # Missing r argument

@pytest.mark.xfail(reason="price not implemented yet")
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