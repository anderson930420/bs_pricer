import math

import pytest

from bs_pricer.curves import PayoffValueCurve, build_payoff_value_curve
from bs_pricer.validation import price_checked


def _curve(option_type: str = "call", **overrides):
    params = {
        "option_type": option_type,
        "K": 100.0,
        "T": 1.0,
        "r": 0.05,
        "sigma": 0.2,
        "spot_min": 80.0,
        "spot_max": 120.0,
        "points": 3,
    }
    params.update(overrides)
    return build_payoff_value_curve(**params)


def test_call_payoff_values_below_at_and_above_strike() -> None:
    curve = _curve("call")

    assert [point.spot for point in curve.points] == [80.0, 100.0, 120.0]
    assert [point.payoff for point in curve.points] == [0.0, 0.0, 20.0]
    assert [point.intrinsic for point in curve.points] == [0.0, 0.0, 20.0]


def test_put_payoff_values_below_at_and_above_strike() -> None:
    curve = _curve("put")

    assert [point.spot for point in curve.points] == [80.0, 100.0, 120.0]
    assert [point.payoff for point in curve.points] == [20.0, 0.0, 0.0]
    assert [point.intrinsic for point in curve.points] == [20.0, 0.0, 0.0]


def test_curve_has_requested_shape_and_selected_option_type() -> None:
    curve = _curve("put", spot_min=50.0, spot_max=150.0, points=11)

    assert isinstance(curve, PayoffValueCurve)
    assert curve.option_type == "put"
    assert len(curve.points) == 11


def test_spot_axis_is_strictly_increasing() -> None:
    curve = _curve(points=9)
    spots = [point.spot for point in curve.points]

    assert all(right > left for left, right in zip(spots, spots[1:]))


def test_first_and_last_spots_match_requested_bounds() -> None:
    curve = _curve(spot_min=75.0, spot_max=125.0, points=6)

    assert curve.points[0].spot == pytest.approx(75.0)
    assert curve.points[-1].spot == pytest.approx(125.0)


def test_call_value_is_at_least_intrinsic_for_normal_inputs() -> None:
    curve = _curve("call", spot_min=70.0, spot_max=130.0, points=7, r=0.0)

    for point in curve.points:
        assert point.value >= point.intrinsic - 1e-10
        assert point.time_value == pytest.approx(point.value - point.intrinsic)


def test_put_value_is_at_least_intrinsic_for_normal_inputs() -> None:
    curve = _curve("put", spot_min=70.0, spot_max=130.0, points=7, r=0.0)

    for point in curve.points:
        assert point.value >= point.intrinsic - 1e-10
        assert point.time_value == pytest.approx(point.value - point.intrinsic)


def test_t_zero_value_equals_payoff() -> None:
    curve = _curve("call", T=0.0)

    for point in curve.points:
        assert point.value == pytest.approx(point.payoff)
        assert point.time_value == pytest.approx(0.0)


def test_sigma_zero_uses_existing_deterministic_pricing_policy() -> None:
    curve = _curve("put", sigma=0.0, T=1.0, r=0.05)

    for point in curve.points:
        expected = price_checked(S=point.spot, K=100.0, sigma=0.0, T=1.0, r=0.05)
        assert math.isfinite(point.value)
        assert point.value == pytest.approx(expected["put"])


@pytest.mark.parametrize("spot_min", [0.0, -1.0])
def test_invalid_spot_min_is_rejected(spot_min: float) -> None:
    with pytest.raises(ValueError, match="spot_min"):
        _curve(spot_min=spot_min)


@pytest.mark.parametrize(
    ("spot_min", "spot_max"),
    [
        (100.0, 100.0),
        (100.0, 99.0),
    ],
)
def test_invalid_spot_max_is_rejected(spot_min: float, spot_max: float) -> None:
    with pytest.raises(ValueError, match="spot_max"):
        _curve(spot_min=spot_min, spot_max=spot_max)


@pytest.mark.parametrize("points", [0, 1])
def test_invalid_points_less_than_two_is_rejected(points: int) -> None:
    with pytest.raises(ValueError, match="points"):
        _curve(points=points)
