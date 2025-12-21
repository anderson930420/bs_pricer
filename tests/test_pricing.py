from unittest import result
import pytest
from bs_pricer.pricing import price
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

