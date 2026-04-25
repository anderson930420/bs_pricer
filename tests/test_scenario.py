import pytest

from bs_pricer.scenario import (
    RESIDUAL_CAVEAT,
    RHO_CAVEAT,
    ScenarioShift,
    ScenarioInputs,
    analyze_scenario,
    apply_shift,
    bridge_rows,
    changed_inputs,
)
from bs_pricer.validation import greeks_checked, price_checked


def test_scenario_shift_transforms_inputs_by_documented_units():
    shift = ScenarioShift(
        name="custom",
        description="custom",
        spot_pct_shift=10.0,
        vol_points_shift=5.0,
        rate_points_shift=1.0,
        days_elapsed=30,
    )

    inputs, reached_expiry = apply_shift(100.0, 100.0, 0.2, 1.0, 0.05, shift)

    assert reached_expiry is False
    assert inputs.S == pytest.approx(110.0)
    assert inputs.sigma == pytest.approx(0.25)
    assert inputs.r == pytest.approx(0.06)
    assert inputs.T == pytest.approx(1.0 - 30.0 / 365.0)


def test_scenario_reaching_expiry_uses_payoff():
    shift = ScenarioShift(name="expiry", description="expiry", spot_pct_shift=10.0, days_elapsed=400)

    result = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=1.0,
        r=0.05,
        option_type="call",
        shift=shift,
    )

    assert result.reached_expiry is True
    assert result.scenario_inputs.T == 0.0
    assert result.scenario_price == pytest.approx(10.0)


def test_negative_volatility_scenario_is_rejected():
    shift = ScenarioShift(name="bad vol", description="bad vol", vol_points_shift=-25.0)

    with pytest.raises(ValueError, match="volatility"):
        apply_shift(100.0, 100.0, 0.2, 1.0, 0.05, shift)


def test_selected_option_type_controls_analyzed_price():
    shift = ScenarioShift(name="spot up", description="spot up", spot_pct_shift=10.0)

    call_result = analyze_scenario(S=100.0, K=100.0, sigma=0.2, T=1.0, r=0.05, option_type="call", shift=shift)
    put_result = analyze_scenario(S=100.0, K=100.0, sigma=0.2, T=1.0, r=0.05, option_type="put", shift=shift)
    call_prices = price_checked(110.0, 100.0, 0.2, 1.0, 0.05)

    assert call_result.option_type == "call"
    assert call_result.selected_option_label == "Long Call"
    assert put_result.option_type == "put"
    assert put_result.selected_option_label == "Long Put"
    assert call_result.scenario_price == pytest.approx(call_prices["call"])
    assert put_result.scenario_price == pytest.approx(call_prices["put"])


def test_bridge_uses_correct_units_and_residual_definition():
    shift = ScenarioShift(
        name="mixed",
        description="mixed",
        spot_pct_shift=10.0,
        vol_points_shift=5.0,
        rate_points_shift=1.0,
        days_elapsed=30,
    )

    result = analyze_scenario(S=100.0, K=100.0, sigma=0.2, T=1.0, r=0.05, option_type="call", shift=shift)
    bridge = result.bridge
    base_greeks = greeks_checked(100.0, 100.0, 0.2, 1.0, 0.05).call

    assert bridge is not None
    assert result.actual_change == pytest.approx(result.scenario_price - result.base_price)
    assert bridge.vega_effect == pytest.approx(base_greeks.vega * 5.0 * 0.01)
    assert bridge.rho_effect == pytest.approx(base_greeks.rho * 1.0 * 0.01)
    assert bridge.theta_effect == pytest.approx(base_greeks.theta * 30.0 / 365.0)
    first_order = bridge.delta_effect + bridge.vega_effect + bridge.theta_effect + bridge.rho_effect
    assert bridge.first_order_approx_change == pytest.approx(first_order)
    assert bridge.residual_change == pytest.approx(result.actual_change - first_order)

    no_spot = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=1.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="vol", description="vol", vol_points_shift=1.0),
    )
    assert no_spot.bridge is not None
    assert no_spot.bridge.vega_effect == pytest.approx(base_greeks.vega * 0.01)
    assert abs(no_spot.bridge.vega_effect) < 1.0


def test_theta_bridge_uses_elapsed_days_over_365():
    one_day = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=1.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="one day", description="one day", days_elapsed=1),
    )
    two_days = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=1.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="two days", description="two days", days_elapsed=2),
    )

    assert one_day.bridge is not None
    assert two_days.bridge is not None
    assert two_days.bridge.theta_effect == pytest.approx(2.0 * one_day.bridge.theta_effect)


def test_scenario_view_data_exposes_selected_option_changed_inputs_and_caveats():
    result = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=1.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="view", description="view", spot_pct_shift=10.0, days_elapsed=30),
    )

    assert result.selected_option_label == "Long Call"
    assert [item.name for item in result.changed_inputs] == ["Spot", "Time to expiry"]
    assert result.changed_inputs[0].display_before == "100.00"
    assert result.changed_inputs[0].display_after == "110.00"
    assert result.rho_caveat == RHO_CAVEAT
    assert result.residual_caveat == RESIDUAL_CAVEAT


def test_analyze_scenario_t_zero_still_prices_without_bridge():
    result = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=0.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="spot up", description="spot up", spot_pct_shift=10.0),
    )

    assert result.base_price == pytest.approx(0.0)
    assert result.scenario_price == pytest.approx(10.0)
    assert result.bridge is None


def test_analyze_scenario_sigma_zero_still_prices_without_bridge():
    result = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.0,
        T=1.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="spot up", description="spot up", spot_pct_shift=10.0),
    )

    assert result.base_price >= 0.0
    assert result.scenario_price >= 0.0
    assert result.bridge is None


def test_valid_base_case_returns_bridge_rows_for_ui_view_data():
    result = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=1.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="spot up", description="spot up", spot_pct_shift=10.0),
    )

    assert result.bridge is not None
    rows = bridge_rows(result)
    assert rows is not None
    assert [row["Component"] for row in rows] == [
        "Delta",
        "Vega",
        "Theta",
        "Rho",
        "First-order approximation",
        "Actual repricing change",
        "Residual",
    ]


def test_bridge_rows_handles_missing_bridge_for_ui_view_data():
    result = analyze_scenario(
        S=100.0,
        K=100.0,
        sigma=0.2,
        T=0.0,
        r=0.05,
        option_type="call",
        shift=ScenarioShift(name="spot up", description="spot up", spot_pct_shift=10.0),
    )

    assert result.bridge is None
    assert bridge_rows(result) is None


def test_changed_inputs_returns_no_fields_when_unchanged():
    inputs = ScenarioInputs(S=100.0, K=100.0, sigma=0.2, T=1.0, r=0.05)

    assert changed_inputs(inputs, inputs) == ()


def test_changed_inputs_returns_one_changed_field():
    base = ScenarioInputs(S=100.0, K=100.0, sigma=0.2, T=1.0, r=0.05)
    scenario = ScenarioInputs(S=110.0, K=100.0, sigma=0.2, T=1.0, r=0.05)

    result = changed_inputs(base, scenario)

    assert [item.name for item in result] == ["Spot"]
    assert result[0].display_before == "100.00"
    assert result[0].display_after == "110.00"


def test_changed_inputs_returns_multiple_changed_fields():
    base = ScenarioInputs(S=100.0, K=100.0, sigma=0.2, T=1.0, r=0.05)
    scenario = ScenarioInputs(S=110.0, K=100.0, sigma=0.25, T=1.0, r=0.06)

    result = changed_inputs(base, scenario)

    assert [item.name for item in result] == ["Spot", "Volatility", "Rate"]
