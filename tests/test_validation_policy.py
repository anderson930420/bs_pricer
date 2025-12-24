import math
import pytest
from bs_pricer.validation import price_checked

def test_reject_zero_S():
    with pytest.raises(ValueError):
        price_checked(0, 100, 0.2, 1.0, 0.05)

def test_reject_negative_S():
    with pytest.raises(ValueError):
        price_checked(-1, 100, 0.2, 1.0, 0.05)

def test_reject_zero_K():
    with pytest.raises(ValueError):
        price_checked(100, 0, 0.2, 1.0, 0.05)  

def test_reject_negative_sigma():
    with pytest.raises(ValueError):
        price_checked(100, 100, -0.1, 1.0, 0.05)

def test_reject_negative_T():
    with pytest.raises(ValueError):
        price_checked(100, 100, 0.2, -1.0, 0.05)

def test_reject_nan_inputs():
    with pytest.raises(ValueError):
        price_checked(math.nan, 100, 0.2, 1.0, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, math.nan, 0.2, 1.0, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, 100, math.nan, 1.0, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, 100, 0.2, math.nan, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, 100, 0.2, 1.0, math.nan)

def test_reject_infinite_inputs():
    with pytest.raises(ValueError):
        price_checked(math.inf, 100, 0.2, 1.0, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, math.inf, 0.2, 1.0, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, 100, math.inf, 1.0, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, 100, 0.2, math.inf, 0.05)

    with pytest.raises(ValueError):
        price_checked(100, 100, 0.2, 1.0, math.inf)

def test_payoff_at_expiry_call_only():
    result = price_checked(120, 100, 0.2, 0.0, 0.05)
    assert result["call"] == 20.0
    assert result["put"] == 0.0

def test_payoff_at_expiry_put_only():
    result = price_checked(80, 100, 0.2, 0.0, 0.05)
    assert result["call"] == 0.0
    assert result["put"] == 20.0

def test_payoff_at_expiry_at_the_money():
    result = price_checked(100, 100, 0.2, 0.0, 0.05)
    assert abs(result["call"]) <= 1e-12
    assert abs(result["put"]) <= 1e-12

def test_deterministic_limit_sigma_zero_call():
    result = price_checked(120, 100, 0.0, 1.0, 0.05)
    pv_k = 100 * math.exp(-0.05 * 1.0)
    expected_call = max(120 - pv_k, 0.0)
    assert abs(result["call"] - expected_call) < 1e-8
    assert abs(result["put"]) <= 1e-12

def test_deterministic_limit_sigma_zero_put():
    result = price_checked(80, 100, 0.0, 1.0, 0.05)
    pv_k = 100 * math.exp(-0.05 * 1.0)
    expected_put = max(pv_k - 80, 0.0)
    assert abs(result["put"] - expected_put) < 1e-8
    assert abs(result["call"]) <= 1e-12

def test_deterministic_limit_sigma_zero_at_the_money(): 
    result = price_checked(100, 100, 0.0, 1.0, 0.05)
    pv_k = 100 * math.exp(-0.05 * 1.0)
    expected_call = max(100 - pv_k, 0.0)
    expected_put = max(pv_k - 100, 0.0)
    assert abs(result["call"] - expected_call) < 1e-8
    assert abs(result["put"] - expected_put) < 1e-8

def test_put_call_parity_holds_when_sigma_zero():
    S, K, T, r = 90.0, 100.0, 1.0, 0.05
    result = price_checked(S, K, 0.0, T, r)
    pv_k = K * math.exp(-r * T)
    lhs = result["call"] - result["put"]
    rhs = S - pv_k
    assert abs(lhs - rhs) < 1e-8