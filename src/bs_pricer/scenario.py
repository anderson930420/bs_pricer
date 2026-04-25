"""Selected-option scenario analysis and Greek price bridge logic."""

from __future__ import annotations

from dataclasses import dataclass

from .validation import greeks_checked, price_checked


RHO_CAVEAT = (
    "Rho is included for completeness, but interest-rate sensitivity is often "
    "small for short-dated options compared with spot, volatility, and time decay."
)
RESIDUAL_CAVEAT = (
    "Residual captures the part of the actual repricing change not explained by "
    "the first-order Greek approximation. This includes nonlinear effects such as gamma."
)


@dataclass(frozen=True)
class ScenarioShift:
    name: str
    description: str
    spot_pct_shift: float = 0.0
    vol_points_shift: float = 0.0
    rate_points_shift: float = 0.0
    days_elapsed: int = 0


@dataclass(frozen=True)
class ScenarioInputs:
    S: float
    K: float
    sigma: float
    T: float
    r: float


@dataclass(frozen=True)
class ChangedInput:
    name: str
    before: float
    after: float
    display_before: str
    display_after: str


@dataclass(frozen=True)
class PriceBridge:
    delta_effect: float
    vega_effect: float
    theta_effect: float
    rho_effect: float
    first_order_approx_change: float
    residual_change: float
    gamma_effect: float | None = None


@dataclass(frozen=True)
class ScenarioResult:
    shift: ScenarioShift
    option_type: str
    selected_option_label: str
    base_inputs: ScenarioInputs
    scenario_inputs: ScenarioInputs
    base_price: float
    scenario_price: float
    actual_change: float
    bridge: PriceBridge | None
    reached_expiry: bool
    changed_inputs: tuple[ChangedInput, ...]
    rho_caveat: str = RHO_CAVEAT
    residual_caveat: str = RESIDUAL_CAVEAT


SCENARIO_PRESETS: tuple[ScenarioShift, ...] = (
    ScenarioShift(
        name="Spot up, vol down",
        description="Underlying rallies while implied volatility falls.",
        spot_pct_shift=10.0,
        vol_points_shift=-2.0,
        days_elapsed=30,
    ),
    ScenarioShift(
        name="Spot down, vol up",
        description="Underlying sells off while implied volatility rises.",
        spot_pct_shift=-10.0,
        vol_points_shift=5.0,
        days_elapsed=30,
    ),
    ScenarioShift(
        name="Time decay",
        description="Calendar time passes with market inputs unchanged.",
        days_elapsed=30,
    ),
    ScenarioShift(
        name="Rates up",
        description="Interest rates increase by one percentage point.",
        rate_points_shift=1.0,
    ),
)


def normalize_option_type(option_type: str) -> str:
    value = str(option_type).strip().lower()
    if value in {"call", "c"}:
        return "call"
    if value in {"put", "p"}:
        return "put"
    raise ValueError("option_type must be 'call' or 'put'")


def selected_option_label(option_type: str) -> str:
    return "Long Call" if normalize_option_type(option_type) == "call" else "Long Put"


def apply_shift(S: float, K: float, sigma: float, T: float, r: float, shift: ScenarioShift) -> tuple[ScenarioInputs, bool]:
    scenario_S = S * (1.0 + shift.spot_pct_shift / 100.0)
    scenario_sigma = sigma + shift.vol_points_shift * 0.01
    scenario_r = r + shift.rate_points_shift * 0.01
    scenario_T = T - shift.days_elapsed / 365.0

    if scenario_sigma < 0:
        raise ValueError("scenario volatility must be non-negative")

    reached_expiry = scenario_T <= 0
    if reached_expiry:
        scenario_T = 0.0

    return ScenarioInputs(
        S=scenario_S,
        K=K,
        sigma=scenario_sigma,
        T=scenario_T,
        r=scenario_r,
    ), reached_expiry


def _fmt_money(value: float) -> str:
    return f"{value:,.2f}"


def _fmt_percent(value: float) -> str:
    return f"{value:.2%}"


def _fmt_days_from_years(value: float) -> str:
    return f"{value * 365.0:.0f} days"


def changed_inputs(base: ScenarioInputs, scenario: ScenarioInputs) -> tuple[ChangedInput, ...]:
    candidates = (
        ChangedInput("Spot", base.S, scenario.S, _fmt_money(base.S), _fmt_money(scenario.S)),
        ChangedInput("Volatility", base.sigma, scenario.sigma, _fmt_percent(base.sigma), _fmt_percent(scenario.sigma)),
        ChangedInput("Rate", base.r, scenario.r, _fmt_percent(base.r), _fmt_percent(scenario.r)),
        ChangedInput("Time to expiry", base.T, scenario.T, _fmt_days_from_years(base.T), _fmt_days_from_years(scenario.T)),
    )
    return tuple(item for item in candidates if item.after != item.before)


def bridge_rows(result: ScenarioResult) -> tuple[dict[str, float | str], ...] | None:
    if result.bridge is None:
        return None

    return (
        {"Component": "Delta", "Effect": result.bridge.delta_effect},
        {"Component": "Vega", "Effect": result.bridge.vega_effect},
        {"Component": "Theta", "Effect": result.bridge.theta_effect},
        {"Component": "Rho", "Effect": result.bridge.rho_effect},
        {"Component": "First-order approximation", "Effect": result.bridge.first_order_approx_change},
        {"Component": "Actual repricing change", "Effect": result.actual_change},
        {"Component": "Residual", "Effect": result.bridge.residual_change},
    )


def analyze_scenario(
    *,
    S: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
    option_type: str,
    shift: ScenarioShift,
) -> ScenarioResult:
    selected = normalize_option_type(option_type)
    base_inputs = ScenarioInputs(S=S, K=K, sigma=sigma, T=T, r=r)
    scenario_inputs, reached_expiry = apply_shift(S, K, sigma, T, r, shift)

    base_prices = price_checked(S, K, sigma, T, r)
    scenario_prices = price_checked(
        scenario_inputs.S,
        scenario_inputs.K,
        scenario_inputs.sigma,
        scenario_inputs.T,
        scenario_inputs.r,
    )
    base_price = float(base_prices[selected])
    scenario_price = float(scenario_prices[selected])
    actual_change = scenario_price - base_price

    try:
        base_greeks = greeks_checked(S, K, sigma, T, r)
    except ValueError:
        bridge = None
    else:
        selected_greeks = getattr(base_greeks, selected)
        delta_spot = scenario_inputs.S - S
        delta_effect = selected_greeks.delta * delta_spot
        vega_effect = selected_greeks.vega * shift.vol_points_shift * 0.01
        theta_effect = selected_greeks.theta * shift.days_elapsed / 365.0
        rho_effect = selected_greeks.rho * shift.rate_points_shift * 0.01
        first_order_approx_change = delta_effect + vega_effect + theta_effect + rho_effect
        residual_change = actual_change - first_order_approx_change
        bridge = PriceBridge(
            delta_effect=delta_effect,
            vega_effect=vega_effect,
            theta_effect=theta_effect,
            rho_effect=rho_effect,
            first_order_approx_change=first_order_approx_change,
            residual_change=residual_change,
        )

    return ScenarioResult(
        shift=shift,
        option_type=selected,
        selected_option_label=selected_option_label(selected),
        base_inputs=base_inputs,
        scenario_inputs=scenario_inputs,
        base_price=base_price,
        scenario_price=scenario_price,
        actual_change=actual_change,
        bridge=bridge,
        reached_expiry=reached_expiry,
        changed_inputs=changed_inputs(base_inputs, scenario_inputs),
    )
