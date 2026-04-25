## Why

The app currently prices call and put options and renders value surfaces, but it does not expose the option's first-order risk sensitivities or explain how a selected option reprices under simple market moves.

## What Changes

- Add a shared scalar Black-Scholes math core for normal CDF/PDF and d1/d2.
- Add Black-Scholes Greeks for call and put options with documented unit conventions.
- Add a checked Greeks API that follows the existing validation policy while rejecting analytic Greeks for expiry and zero-volatility cases.
- Add selected-option scenario analysis with MVP scenario presets, input transformations, repricing, and first-order Greek bridge decomposition.
- Add Streamlit tabs for Price & Greeks, Scenario Analysis, and Surfaces.

## Impact

- New modules: `src/bs_pricer/_bs_core.py`, `src/bs_pricer/greeks.py`, `src/bs_pricer/scenario.py`.
- Existing scalar pricing delegates shared d1/d2 and CDF helpers to the scalar core.
- Streamlit UI gains Greek cards and scenario analysis while keeping formulas outside the UI layer.
- Tests cover Greek conventions, scenario transformations, bridge decomposition, and pricing regression behavior.
