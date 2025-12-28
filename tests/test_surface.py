import math
import numpy as np

from bs_pricer.surface import value_surface
from bs_pricer.validation import price_checked

def test_value_surface_shapes():
    S_axis = np.array([80.0, 90.0, 100.0])
    sigma_axis = np.array([0.1, 0.2])
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=K,
        T=T,
        r=r,
    )

    assert vs.call.shape == (len(sigma_axis), len(S_axis))
    assert vs.put.shape == vs.call.shape

    # axes preserved
    assert np.all(vs.S_axis == S_axis)
    assert np.all(vs.sigma_axis == sigma_axis)

def test_value_surface_matches_engine_at_sample_point():
    S_axis = np.array([80.0, 100.0, 120.0])
    sigma_axis = np.array([0.1, 0.3])
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=K,
        T=T,
        r=r,
    )

    i, j = 1, 2  # sigma=0.3, S=120
    expected = price_checked(S_axis[j], K, sigma_axis[i], T, r)

    assert abs(vs.call[i, j] - expected["call"]) < 1e-10
    assert abs(vs.put[i, j] - expected["put"]) < 1e-10

def test_put_call_parity_holds_on_surface():
    S_axis = np.array([80.0, 90.0, 100.0, 110.0])
    sigma_axis = np.array([0.1, 0.2, 0.3])
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=K,
        T=T,
        r=r,
    )

    pv_k = K * math.exp(-r * T)

    lhs = vs.call - vs.put                    # shape (nV, nS)
    rhs = vs.S_axis - pv_k                    # shape (nS,)
    rhs = rhs[None, :]                        # broadcast

    assert np.max(np.abs(lhs - rhs)) < 1e-10

def test_call_is_monotone_in_S():
    S_axis = np.linspace(50.0, 150.0, 51)
    sigma_axis = np.array([0.2])
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=K,
        T=T,
        r=r,
    )

    call_row = vs.call[0]
    diffs = np.diff(call_row)

    assert np.all(diffs >= -1e-10)

def test_call_and_put_are_monotone_in_sigma():
    S_axis = np.array([80.0, 100.0, 120.0])
    sigma_axis = np.linspace(0.05, 0.6, 30)
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=K,
        T=T,
        r=r,
    )

    # fixed S = 100
    j = 1

    call_col = vs.call[:, j]
    put_col = vs.put[:, j]

    assert np.all(np.diff(call_col) >= -1e-10)
    assert np.all(np.diff(put_col) >= -1e-10)

def test_T_zero_surface_equals_payoff_and_is_sigma_invariant():
    S_axis = np.array([80.0, 100.0, 120.0])
    sigma_axis = np.array([0.0, 0.2, 1.0])
    K, T, r = 100.0, 0.0, 0.05

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=K,
        T=T,
        r=r,
    )

    expected_call = np.maximum(S_axis - K, 0.0)
    expected_put = np.maximum(K - S_axis, 0.0)

    for i in range(len(sigma_axis)):
        assert np.allclose(vs.call[i], expected_call, atol=1e-12)
        assert np.allclose(vs.put[i], expected_put, atol=1e-12)

def test_sigma_zero_row_matches_deterministic_limit():
    S_axis = np.array([80.0, 100.0, 120.0])
    sigma_axis = np.array([0.0, 0.3])
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=K,
        T=T,
        r=r,
    )

    pv_k = K * math.exp(-r * T)
    expected_call = np.maximum(S_axis - pv_k, 0.0)
    expected_put = np.maximum(pv_k - S_axis, 0.0)

    assert np.allclose(vs.call[0], expected_call, atol=1e-10)
    assert np.allclose(vs.put[0], expected_put, atol=1e-10)
