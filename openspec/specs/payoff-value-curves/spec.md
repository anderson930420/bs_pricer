# payoff-value-curves Specification

## Purpose
TBD - created by archiving change add-payoff-and-value-curves. Update Purpose after archive.
## Requirements
### Requirement: Payoff and value curve data is available from the domain layer
The package MUST expose a Streamlit-independent curve builder for selected call or put options.

#### Scenario: Curve builder returns stable selected-option rows
- **WHEN** payoff/value curve data is built for option type `call` or `put`
- **THEN** the result identifies the selected option type
- **AND** it contains exactly the requested number of rows
- **AND** each row includes spot, expiration payoff, current theoretical value, intrinsic value, and time value

#### Scenario: Curve builder uses existing checked pricing policy
- **WHEN** current theoretical values are computed across the spot axis
- **THEN** the builder uses the existing checked pricing API
- **AND** it does not duplicate Black-Scholes pricing formulas
- **AND** existing `T == 0` and `sigma == 0` pricing policies are preserved

### Requirement: Payoff and intrinsic values follow option-side contracts
The curve builder MUST compute payoff and intrinsic values for the selected option side.

#### Scenario: Call payoff and intrinsic values are max spot minus strike
- **WHEN** a call curve is built with spots below, at, and above strike
- **THEN** payoff equals `max(S - K, 0)`
- **AND** intrinsic value equals `max(S - K, 0)`

#### Scenario: Put payoff and intrinsic values are max strike minus spot
- **WHEN** a put curve is built with spots below, at, and above strike
- **THEN** payoff equals `max(K - S, 0)`
- **AND** intrinsic value equals `max(K - S, 0)`

#### Scenario: Time value is the theoretical value less intrinsic value
- **WHEN** a curve point is returned
- **THEN** time value equals current theoretical value minus intrinsic value

### Requirement: Curve axis inputs are validated
The curve builder MUST validate curve-specific axis inputs before producing rows.

#### Scenario: Spot axis is strictly increasing and honors requested bounds
- **WHEN** a curve is built with positive `spot_min`, larger `spot_max`, and at least two points
- **THEN** the spot axis is strictly increasing
- **AND** the first row spot equals `spot_min`
- **AND** the last row spot equals `spot_max`

#### Scenario: Invalid spot bounds are rejected
- **WHEN** `spot_min <= 0`
- **THEN** the curve request is rejected
- **WHEN** `spot_max <= spot_min`
- **THEN** the curve request is rejected

#### Scenario: Invalid point count is rejected
- **WHEN** fewer than two points are requested
- **THEN** the curve request is rejected

### Requirement: Streamlit exposes payoff and value curves
The Streamlit app MUST provide an interactive payoff/value curve visualization without embedding domain formulas in the UI.

#### Scenario: Curve tab renders selected option curves
- **WHEN** the app inputs are valid
- **THEN** users can select call or put curve analysis
- **AND** users can configure spot range and point count
- **AND** the UI plots current theoretical value and payoff at expiration
- **AND** the UI may also plot intrinsic value or time value when visually clear

#### Scenario: Curve tab explains the displayed series
- **WHEN** the curve section is rendered
- **THEN** it labels payoff as payoff at expiration
- **AND** it labels Black-Scholes value as current theoretical value
- **AND** it explains that time value is the gap between theoretical value and intrinsic value before expiry

#### Scenario: Curve tab handles invalid inputs gracefully
- **WHEN** curve-specific validation fails
- **THEN** the UI displays an error for the curve section
- **AND** it does not crash the rest of the app

