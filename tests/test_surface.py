import ast
import math
from pathlib import Path
import inspect
import numpy as np

from bs_pricer import surface as surface_module
from bs_pricer.surface import value_surface, value_surface_fast
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


def test_value_surface_still_accepts_engine_injection() -> None:
    calls: list[tuple[float, float, float, float, float]] = []

    def engine(S: float, K: float, sigma: float, T: float, r: float) -> dict[str, float]:
        calls.append((S, K, sigma, T, r))
        return {"call": S + K + sigma + T + r, "put": S - K + sigma - T - r}

    S_axis = np.array([80.0, 100.0])
    sigma_axis = np.array([0.1, 0.2])

    vs = value_surface(
        S_axis=S_axis,
        sigma_axis=sigma_axis,
        K=100.0,
        T=1.0,
        r=0.05,
        engine=engine,
    )

    assert len(calls) == len(S_axis) * len(sigma_axis)
    np.testing.assert_allclose(vs.call, np.array([[181.15, 201.15], [181.25, 201.25]]))
    np.testing.assert_allclose(vs.put, np.array([[-20.95, -0.95], [-20.85, -0.85]]))


def test_value_surface_fast_shape_and_order_match_scalar() -> None:
    S_axis = np.array([80.0, 100.0, 120.0])
    sigma_axis = np.array([0.0, 0.15, 0.3])
    K, T, r = 100.0, 1.0, 0.05

    scalar_vs = value_surface(S_axis=S_axis, sigma_axis=sigma_axis, K=K, T=T, r=r)
    fast_vs = value_surface_fast(S_axis=S_axis, sigma_axis=sigma_axis, K=K, T=T, r=r)

    assert isinstance(fast_vs, type(scalar_vs))
    assert fast_vs.call.shape == scalar_vs.call.shape
    assert fast_vs.put.shape == scalar_vs.put.shape
    assert np.all(fast_vs.S_axis == scalar_vs.S_axis)
    assert np.all(fast_vs.sigma_axis == scalar_vs.sigma_axis)


def test_value_surface_fast_matches_scalar_at_selected_points() -> None:
    S_axis = np.array([80.0, 90.0, 100.0, 110.0, 120.0])
    sigma_axis = np.array([0.0, 0.1, 0.3, 0.6])
    K, T, r = 100.0, 1.0, 0.05

    scalar_vs = value_surface(S_axis=S_axis, sigma_axis=sigma_axis, K=K, T=T, r=r)
    fast_vs = value_surface_fast(S_axis=S_axis, sigma_axis=sigma_axis, K=K, T=T, r=r)

    np.testing.assert_allclose(fast_vs.call, scalar_vs.call, atol=1e-10, rtol=1e-12)
    np.testing.assert_allclose(fast_vs.put, scalar_vs.put, atol=1e-10, rtol=1e-12)


def test_value_surface_fast_handles_t_zero_without_nan_or_inf() -> None:
    S_axis = np.array([80.0, 100.0, 120.0])
    sigma_axis = np.array([0.0, 0.2, 1.0])
    K, T, r = 100.0, 0.0, 0.05

    vs = value_surface_fast(S_axis=S_axis, sigma_axis=sigma_axis, K=K, T=T, r=r)

    expected_call = np.maximum(S_axis - K, 0.0)
    expected_put = np.maximum(K - S_axis, 0.0)

    assert np.isfinite(vs.call).all()
    assert np.isfinite(vs.put).all()
    for i in range(len(sigma_axis)):
        np.testing.assert_allclose(vs.call[i], expected_call, atol=1e-12, rtol=0.0)
        np.testing.assert_allclose(vs.put[i], expected_put, atol=1e-12, rtol=0.0)


def test_value_surface_fast_handles_sigma_zero_without_nan_or_inf() -> None:
    S_axis = np.array([80.0, 100.0, 120.0])
    sigma_axis = np.array([0.0, 0.2, 0.6])
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface_fast(S_axis=S_axis, sigma_axis=sigma_axis, K=K, T=T, r=r)

    discounted_K = K * math.exp(-r * T)
    expected_call = np.maximum(S_axis - discounted_K, 0.0)
    expected_put = np.maximum(discounted_K - S_axis, 0.0)

    assert np.isfinite(vs.call).all()
    assert np.isfinite(vs.put).all()
    np.testing.assert_allclose(vs.call[0], expected_call, atol=1e-10, rtol=1e-12)
    np.testing.assert_allclose(vs.put[0], expected_put, atol=1e-10, rtol=1e-12)


def test_value_surface_fast_put_call_parity() -> None:
    S_axis = np.array([80.0, 95.0, 110.0, 130.0])
    sigma_axis = np.array([0.0, 0.15, 0.4])
    K, T, r = 100.0, 1.0, 0.05

    vs = value_surface_fast(S_axis=S_axis, sigma_axis=sigma_axis, K=K, T=T, r=r)

    pv_k = K * math.exp(-r * T)
    expected = vs.S_axis - pv_k
    np.testing.assert_allclose(
        vs.call - vs.put,
        np.broadcast_to(expected[None, :], vs.call.shape),
        atol=1e-10,
        rtol=1e-12,
    )


def test_surface_module_stays_explicit_axis_only() -> None:
    source = Path(surface_module.__file__).read_text()
    tree = ast.parse(source)

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert "bs_pricer.config" not in imported_modules
    assert "config" not in imported_modules
    assert "np.where" not in source


def test_value_surface_fast_has_no_engine_parameter() -> None:
    sig = inspect.signature(value_surface_fast)
    assert "engine" not in sig.parameters

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
