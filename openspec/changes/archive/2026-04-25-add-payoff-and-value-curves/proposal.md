## Why

The app already supports point-in-time Black-Scholes pricing, Greeks, scenarios, and value surfaces, but it does not show the one-dimensional relationship between spot price, expiration payoff, and current theoretical value. A focused curve view will make call/put behavior easier to inspect and demonstrate before implied volatility work.

## What Changes

Add a dedicated domain curve builder for a selected call or put option. The builder returns stable, UI-ready data points over a strictly increasing spot axis, including expiration payoff, current checked Black-Scholes value, intrinsic value, and time value.

Expose the curve in Streamlit as a new payoff/value visualization tab that reuses the app's current option inputs and renders prepared curve data without embedding pricing formulas in the UI.

## Capabilities

### New Capabilities
- `payoff-value-curves`: construct and render selected-option payoff and value curves

## Impact

- `src/bs_pricer/curves.py`
- `src/bs_pricer/app_streamlit.py`
- `tests/test_curves.py`
- `README.md`
- `openspec/specs/payoff-value-curves/spec.md` after archive
