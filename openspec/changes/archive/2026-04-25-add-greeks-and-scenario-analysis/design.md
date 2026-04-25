## Architecture

The implementation keeps domain math out of Streamlit. Scalar Black-Scholes primitives live in `_bs_core.py`; pricing uses them for prices; `greeks.py` uses them for analytic Greeks; `validation.py` owns input validation policy; `scenario.py` owns scenario models, presets, input shifting, repricing, and first-order price bridge logic.

## Scalar Core

`_bs_core.py` is scalar-only and uses `math`. It may import `scipy.special.ndtr` for `norm_cdf`, but it must not import NumPy or own validation, scenario logic, charting, or UI formatting.

## Greek Conventions

The Greeks data model is:

- `GreekValues(delta, gamma, vega, theta, rho)`
- `Greeks(call, put)`

Access style is `greeks.call.delta` and `greeks.put.theta`.

Internal unit conventions are:

- Delta: `dV/dS`.
- Gamma: `d2V/dS2`.
- Vega: `dV/dsigma`, where sigma is decimal volatility such as `0.20`.
- Theta: market-convention theta, `-dV/dT`, representing value change as calendar time passes with other inputs held constant.
- Rho: `dV/dr`, where rate is decimal such as `0.05`.

Displayed conversions are view-layer conversions:

- daily theta: `theta / 365.0`
- vega per volatility point: `vega * 0.01`
- rho per rate point: `rho * 0.01`

Analytic Greeks require `T > 0` and `sigma > 0`. Pricing remains available for `T == 0` and `sigma == 0` using the existing pricing policy, but the checked Greeks API rejects those analytic edge cases.

## Scenario Analysis

`scenario.py` owns scenario domain concepts. Presets are module-level constants there, not config values.

Scenario shifts use:

- `spot_pct_shift`: `10.0` means spot increases by 10%.
- `vol_points_shift`: `5.0` means volatility increases by `0.05`.
- `rate_points_shift`: `1.0` means rate increases by `0.01`.
- `days_elapsed`: `30` means 30 calendar days pass.

Input transformation:

- `scenario_S = S * (1 + spot_pct_shift / 100.0)`
- `scenario_sigma = sigma + vol_points_shift * 0.01`
- `scenario_r = r + rate_points_shift * 0.01`
- `scenario_T = T - days_elapsed / 365.0`

Negative volatility is invalid. If transformed `T <= 0`, the scenario reaches expiry and reprices using expiration payoff instead of silently pricing with negative time.

## Price Bridge

Scenario analysis follows the selected option type. Base-case Greeks, not scenario-case Greeks, feed the first-order bridge:

- `delta_effect = delta * delta_spot`
- `vega_effect = vega * vol_points_shift * 0.01`
- `theta_effect = theta * days_elapsed / 365.0`
- `rho_effect = rho * rate_points_shift * 0.01`

The first-order approximation is the sum of those effects. Residual change is the actual repricing change minus the first-order approximation. MVP does not report a separate gamma effect; the residual captures gamma, cross-Greek, and higher-order repricing effects.

## Streamlit

The UI presents:

- Tab 1: Price & Greeks
- Tab 2: Scenario Analysis
- Tab 3: Surfaces

The UI may format values, choose selected option type, and render tables, but it must not contain Greek formulas or scenario bridge decomposition logic.
