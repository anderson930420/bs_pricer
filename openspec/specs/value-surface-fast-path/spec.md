# value-surface-fast-path Specification

## Purpose
TBD - created by archiving change optimize-value-surface-vectorized-path. Update Purpose after archive.
## Requirements
### Requirement: Vectorized surface generation is available as a separate path
The surface layer MUST expose a separate vectorized NumPy path for generating option value surfaces from explicit axes.

#### Scenario: Fast path returns the same surface shape contract
- **WHEN** `value_surface_fast` is called with explicit `S_axis` and `sigma_axis`
- **THEN** it returns a `ValueSurface` object
- **AND** the call and put matrices use the same axis ordering and shapes as the canonical scalar surface path

#### Scenario: Fast path preserves expiry policy
- **WHEN** `T = 0`
- **THEN** the fast path returns intrinsic call and put values
- **AND** it does not produce NaN or infinity values

#### Scenario: Fast path preserves sigma-zero deterministic policy
- **WHEN** `T > 0` and `sigma_axis` includes zero
- **THEN** the fast path uses the discounted-strike deterministic limit for zero-volatility cells
- **AND** it does not produce NaN or infinity values

#### Scenario: Fast path matches scalar surface values
- **WHEN** the same explicit axes and pricing parameters are supplied to `value_surface` and `value_surface_fast`
- **THEN** the resulting surfaces agree within tolerance at selected grid points

### Requirement: Canonical scalar surface path remains unchanged
The existing scalar `value_surface(...)` API MUST remain available as the engine-injected correctness path.

#### Scenario: Engine injection remains supported
- **WHEN** `value_surface` is called with a custom engine
- **THEN** the scalar path continues to use that engine

### Requirement: Surface layer remains explicit-axis only
The surface module MUST remain free of configuration coupling.

#### Scenario: Surface module stays decoupled from config
- **WHEN** the surface module is inspected
- **THEN** it does not import `config.py`

