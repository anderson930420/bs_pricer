import ast
import math

from pathlib import Path

import numpy as np
import pytest

from bs_pricer import validation as validation_module
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


def test_accepts_numpy_scalar_numbers() -> None:
    result = price_checked(
        np.float64(120.0),
        np.int64(100),
        np.float64(0.2),
        np.float64(1.0),
        np.float64(0.05),
    )

    baseline = price_checked(120.0, 100.0, 0.2, 1.0, 0.05)

    assert result["call"] == pytest.approx(baseline["call"])
    assert result["put"] == pytest.approx(baseline["put"])


def test_rejects_bool_string_and_non_real_inputs() -> None:
    with pytest.raises(TypeError):
        price_checked(True, 100, 0.2, 1.0, 0.05)

    with pytest.raises(TypeError):
        price_checked(100, "100", 0.2, 1.0, 0.05)

    with pytest.raises(TypeError):
        price_checked(100, 100, object(), 1.0, 0.05)


def test_validation_helper_uses_bool_first_real_then_finite_order() -> None:
    source = Path(validation_module.__file__).read_text()
    tree = ast.parse(source)

    helper = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_is_finite_real_number"
    )

    first_if = helper.body[0]
    second_if = helper.body[1]
    third_stmt = helper.body[2]

    assert isinstance(first_if, ast.If)
    assert isinstance(second_if, ast.If)
    assert isinstance(third_stmt, ast.Return)
    assert "bool" in ast.unparse(first_if.test)
    assert "numbers.Real" in ast.unparse(second_if.test)
    assert "math.isfinite(float(value))" in ast.unparse(third_stmt.value)

    source_text = source.replace(" ", "")
    assert "(int,float)" not in source_text

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
