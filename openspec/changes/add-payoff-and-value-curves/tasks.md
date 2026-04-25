## 1. Domain Curve Builder

- [x] 1.1 Add a dedicated curve domain module with immutable curve point/result models.
- [x] 1.2 Build a strictly increasing spot axis from explicit positive bounds and point count.
- [x] 1.3 Compute selected-option payoff, checked Black-Scholes value, intrinsic value, and time value without duplicating Black-Scholes formulas.

## 2. Regression Coverage

- [x] 2.1 Add domain tests for call and put payoff values below, at, and above strike.
- [x] 2.2 Add shape, axis ordering, endpoint, and invalid input tests.
- [x] 2.3 Add tests for value/intrinsic relationships and existing `T == 0` / `sigma == 0` pricing policies.

## 3. Streamlit Integration

- [x] 3.1 Add a Payoff & Value Curves tab or equivalent section to the app.
- [x] 3.2 Reuse current app option inputs and expose curve range/point controls.
- [x] 3.3 Render prepared curve data with graceful validation error handling and no Streamlit-specific logic in the domain module.

## 4. Documentation and Validation

- [x] 4.1 Update README feature and app usage documentation.
- [x] 4.2 Run OpenSpec validation, tests, and CLI smoke commands.
