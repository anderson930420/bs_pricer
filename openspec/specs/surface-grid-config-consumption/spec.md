# surface-grid-config-consumption Specification

## Purpose
TBD - created by archiving change stabilize-surface-grid-config-consumption. Update Purpose after archive.
## Requirements
### Requirement: Canonical grid config drives surface UI defaults
The Streamlit surface UI MUST derive its heatmap defaults from the canonical `GRID_CONFIG` contract in `config.py` rather than from stale key names.

#### Scenario: Canonical keys provide heatmap defaults
- **WHEN** the app boundary reads grid configuration
- **THEN** it uses `SPOT_MIN_PCT`, `SPOT_MAX_PCT`, `SPOT_STEPS`, `VOL_MIN`, `VOL_MAX`, and `VOL_STEPS`
- **AND** it can derive concrete spot and volatility defaults without requiring legacy keys such as `S_min` or `sigma_min`

#### Scenario: Updated canonical values change generated defaults
- **WHEN** canonical `GRID_CONFIG` values change
- **THEN** the app boundary produces different heatmap defaults and axes from those updated values

### Requirement: Surface generation remains explicit-axis only
The surface layer MUST continue to accept explicit `S_axis` and `sigma_axis` inputs and MUST NOT import `config.py`.

#### Scenario: Surface layer stays decoupled from config
- **WHEN** the surface module is inspected for dependencies
- **THEN** it does not import `config.py`
- **AND** it continues to generate values from provided axes only

