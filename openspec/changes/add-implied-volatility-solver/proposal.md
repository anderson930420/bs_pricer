## Why

The app can compute theoretical Black-Scholes option prices from volatility, but it cannot invert a market option price back to the volatility implied by the same model.

## What Changes

- Add a dedicated implied-volatility domain module for single European call/put calibration under the existing no-dividend Black-Scholes model.
- Use bisection over volatility and reuse the existing checked pricing path instead of duplicating pricing formulas.
- Validate market prices against no-arbitrage bounds, including deterministic sigma-zero lower bounds.
- Return solver diagnostics: solved volatility, model price, price error, iterations, and valid bounds.
- Add a small Streamlit implied-volatility tab that collects market price and renders solver results or validation errors.
- Update README feature documentation.

## Impact

- New module: `src/bs_pricer/implied_vol.py`.
- New tests: `tests/test_implied_vol.py`.
- Streamlit gains an implied-volatility workflow without numerical solver logic in the UI.
- No support is added for smiles, surfaces, dividends, American options, option chains, or multi-leg strategies.
