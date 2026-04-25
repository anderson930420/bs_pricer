# option-risk-analysis Specification

## Purpose
TBD - created by archiving change add-greeks-and-scenario-analysis. Update Purpose after archive.
## Requirements
### Requirement: Scalar Black-Scholes core is shared by pricing and Greeks
The app MUST provide a scalar-only Black-Scholes core for reusable normal distribution and d1/d2 helpers.

#### Scenario: Scalar core exposes normal distribution helpers
- **WHEN** the scalar core is imported
- **THEN** it exposes `norm_cdf(x)` and `norm_pdf(x)`
- **AND** `norm_pdf(0)` equals `1 / sqrt(2*pi)` within tolerance
- **AND** the module does not import NumPy

#### Scenario: Pricing delegates scalar d1/d2 logic
- **WHEN** scalar pricing computes standard Black-Scholes prices
- **THEN** it uses shared scalar d1/d2 logic
- **AND** existing public pricing behavior is preserved

### Requirement: Greeks domain model exposes call and put values
The risk layer MUST expose frozen Greek domain models for call and put option sensitivities.

#### Scenario: Greek values are accessible by option side
- **WHEN** Greeks are computed for valid analytic inputs
- **THEN** callers can access `greeks.call.delta`
- **AND** callers can access `greeks.put.theta`
- **AND** the outer dataclass is named `Greeks`

### Requirement: Greek unit conventions are documented and enforced
Greeks MUST use explicit Black-Scholes unit conventions.

#### Scenario: Analytic Greeks follow required conventions
- **WHEN** Greeks are computed for standard long vanilla option inputs
- **THEN** call delta is positive
- **AND** put delta is negative
- **AND** gamma is positive
- **AND** call and put gamma are identical within tolerance
- **AND** call and put vega are identical within tolerance
- **AND** market-convention theta is typically negative for normal long vanilla options
- **AND** call rho is positive under standard conditions
- **AND** put rho is negative under standard conditions

#### Scenario: Vega and rho use decimal units internally
- **WHEN** scenario bridge effects are computed
- **THEN** vega uses decimal volatility shifts such that one volatility point is `0.01`
- **AND** rho uses decimal rate shifts such that one rate point is `0.01`

#### Scenario: Theta uses market convention
- **WHEN** theta is reported by the Greeks API
- **THEN** theta means `-dV/dT`
- **AND** it represents the option value change as calendar time passes while other inputs are held constant

### Requirement: Checked Greeks API preserves validation policy
The validation layer MUST provide a checked Greeks API consistent with existing input validation.

#### Scenario: Checked Greeks reject non-analytic edge cases
- **WHEN** checked Greeks are requested with `T == 0`
- **THEN** the request is rejected instead of fabricating analytic Greeks
- **WHEN** checked Greeks are requested with `sigma == 0`
- **THEN** the request is rejected instead of fabricating analytic Greeks

#### Scenario: Pricing remains available for deterministic cases
- **WHEN** pricing is requested with `T == 0` or `sigma == 0`
- **THEN** existing checked pricing policy still returns valid prices

### Requirement: Selected-option scenario analysis is available
The scenario layer MUST compute scenario repricing for the selected option type.

#### Scenario: Scenario shifts transform inputs by documented units
- **WHEN** a scenario has spot, volatility, rate, and day shifts
- **THEN** spot changes by percentage
- **AND** volatility changes by volatility points converted to decimal volatility
- **AND** rate changes by rate points converted to decimal rate
- **AND** time to expiry decreases by elapsed calendar days divided by 365

#### Scenario: Scenario follows selected option side
- **WHEN** selected option type is call
- **THEN** scenario price, P&L, and bridge effects are computed for the call
- **WHEN** selected option type is put
- **THEN** scenario price, P&L, and bridge effects are computed for the put

#### Scenario: Scenario handles invalid and expiry states
- **WHEN** transformed volatility is negative
- **THEN** the scenario is rejected or marked invalid
- **WHEN** transformed time to expiry is less than or equal to zero
- **THEN** the scenario reaches expiry and uses expiration payoff
- **AND** negative time is not silently passed into Black-Scholes pricing

### Requirement: First-order Greek price bridge decomposes repricing
Scenario results MUST include a first-order bridge from base-case Greeks and residual repricing effect.

#### Scenario: Bridge effects use base Greeks and correct units
- **WHEN** a scenario result is computed
- **THEN** actual change equals scenario price minus base price
- **AND** delta effect equals base delta times spot change
- **AND** vega effect equals base vega times `vol_points_shift * 0.01`
- **AND** theta effect equals base market-convention theta times `days_elapsed / 365.0`
- **AND** rho effect equals base rho times `rate_points_shift * 0.01`
- **AND** residual equals actual change minus the first-order approximation

#### Scenario: Residual represents nonlinear repricing
- **WHEN** residual is displayed
- **THEN** it is described as the part of actual repricing not explained by first-order Greeks
- **AND** it includes nonlinear effects such as gamma
- **AND** MVP does not separately display gamma effect

### Requirement: Streamlit UI exposes option risk analysis
The Streamlit app MUST provide tabs for price, scenarios, and surfaces without embedding domain formulas in the UI.

#### Scenario: Price and Greeks tab renders values and conversions
- **WHEN** the app has valid analytic Greek inputs
- **THEN** it shows call and put price cards
- **AND** it shows Greek cards
- **AND** it shows daily theta
- **AND** it shows vega per volatility point
- **AND** it shows rho per rate point

#### Scenario: Price and Greeks tab handles unavailable Greeks
- **WHEN** `T == 0` or `sigma == 0`
- **THEN** valid prices remain visible
- **AND** the UI indicates analytic Greeks are unavailable

#### Scenario: Scenario tab exposes selected option and changed inputs
- **WHEN** scenario analysis is rendered
- **THEN** the selected option type is visibly shown inside the tab
- **AND** the base price is shown
- **AND** preset scenario controls are shown
- **AND** changed inputs are shown with before and after values
- **AND** scenario result and bridge decomposition are shown
- **AND** rho and residual caveats are available to render

