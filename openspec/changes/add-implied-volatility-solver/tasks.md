## 1. OpenSpec

- [x] 1.1 Create proposal, tasks, and implied-volatility spec delta.
- [x] 1.2 Validate the change with `openspec validate add-implied-volatility-solver --type change --no-interactive`.

## 2. Domain Solver

- [x] 2.1 Add `src/bs_pricer/implied_vol.py` with `ImpliedVolatilityResult`.
- [x] 2.2 Implement bisection-based `solve_implied_volatility` using existing checked pricing.
- [x] 2.3 Validate solver parameters, expiry, market price bounds, and bracketing failures.

## 3. Tests

- [x] 3.1 Add solver tests for call/put recovery, lower-bound zero IV, invalid bounds, diagnostics, invalid parameters, and a valid deep moneyness case.

## 4. Streamlit UI

- [x] 4.1 Add an Implied Volatility tab or section using current base inputs and no embedded solver logic.
- [x] 4.2 Display implied volatility diagnostics and validation messages.

## 5. Documentation

- [x] 5.1 Update README feature and usage text without claiming unsupported calibration features.

## 6. Verification

- [x] 6.1 Run OpenSpec validation.
- [x] 6.2 Run `python3 -m pytest`.
- [x] 6.3 Run `python3 -m bs_pricer --help`, `python3 -m bs_pricer price --help`, and `python3 -m bs_pricer price --no-persist`.
- [x] 6.4 Run a Streamlit smoke check when available.
