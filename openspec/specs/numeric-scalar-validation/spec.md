# numeric-scalar-validation Specification

## Purpose
TBD - created by archiving change stabilize-numeric-scalar-validation. Update Purpose after archive.
## Requirements
### Requirement: Scalar validation accepts finite real numeric scalars
The pricing validation layer MUST accept finite real scalar numeric inputs, including numpy scalar real numbers, while rejecting invalid scalar forms.

#### Scenario: Numpy scalar inputs are accepted
- **WHEN** `price_checked` receives `numpy.float64` and `numpy.int64` values that satisfy the domain rules
- **THEN** validation succeeds
- **AND** the pricing result is produced normally

#### Scenario: Bool and non-real inputs are rejected
- **WHEN** `price_checked` receives `bool`, `NaN`, infinity, strings, or non-real objects
- **THEN** validation fails before pricing

### Requirement: Existing pricing domain policies remain unchanged
The validation layer MUST preserve existing domain constraints and special-case pricing behavior.

#### Scenario: Expiry policy remains intact
- **WHEN** `T = 0`
- **THEN** the payoff-at-expiry policy is preserved

#### Scenario: Deterministic limit remains intact
- **WHEN** `sigma = 0` and `T > 0`
- **THEN** the deterministic-limit policy is preserved

