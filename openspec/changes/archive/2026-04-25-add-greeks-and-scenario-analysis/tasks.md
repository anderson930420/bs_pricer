## 1. OpenSpec

- [x] 1.1 Create proposal, design, tasks, and option-risk-analysis spec.
- [x] 1.2 Validate the change with `openspec validate add-greeks-and-scenario-analysis --type change --no-interactive`.

## 2. Scalar Core And Pricing

- [x] 2.1 Add scalar `_bs_core.py` with `norm_cdf`, required `norm_pdf`, and `d1_d2`.
- [x] 2.2 Refactor `pricing.py` to use the shared scalar core while preserving public pricing behavior.

## 3. Greeks

- [x] 3.1 Add `GreekValues` and `Greeks` dataclasses.
- [x] 3.2 Implement call and put Black-Scholes Greeks using the shared scalar core.
- [x] 3.3 Add checked Greeks API in the validation layer for valid analytic cases only.

## 4. Scenario Analysis

- [x] 4.1 Add scenario domain models, MVP presets, input shifting, selected-option repricing, and expiry handling.
- [x] 4.2 Add first-order Greek price bridge decomposition and residual repricing effect.
- [x] 4.3 Expose Streamlit-facing scenario view data, including selected option type, changed inputs, rho caveat, and residual caveat.

## 5. Tests

- [x] 5.1 Add shared core and pricing regression tests.
- [x] 5.2 Add Greek convention and checked API tests.
- [x] 5.3 Add scenario transformation, selected-option, bridge, expiry, invalid volatility, and view data tests.

## 6. Streamlit UI

- [x] 6.1 Refactor Streamlit into Price & Greeks, Scenario Analysis, and Surfaces tabs.
- [x] 6.2 Render Greek display conversions and gracefully handle unavailable Greeks.
- [x] 6.3 Render selected-option scenario analysis, changed inputs, result table, bridge decomposition, and caveats.

## 7. Verification

- [x] 7.1 Run the full test suite with `pytest`.
- [x] 7.2 Run OpenSpec validation again.
