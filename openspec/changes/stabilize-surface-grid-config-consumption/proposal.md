## Why

The Streamlit surface view is reading stale grid keys that no longer match the canonical `GRID_CONFIG` contract in `config.py`. That creates a silent fallback path where the UI can ignore the configured surface ranges and resolution.

## What Changes

The Streamlit boundary will consume canonical grid settings through a small helper that converts `GRID_CONFIG` into concrete heatmap defaults. The helper will derive spot defaults from the current spot input and the canonical percentage bounds, while volatility bounds and grid density continue to come from `GRID_CONFIG`.

`surface.py` will remain unchanged as the surface calculator for explicit axes. The app layer will stop reading stale grid keys and will rely on the helper instead.

## Capabilities

### New Capabilities
- `surface-grid-config-consumption`: translate canonical grid config into UI defaults and surface axes without depending on stale key names

## Impact

- `src/bs_pricer/app_streamlit.py`
- `src/bs_pricer/surface_grid.py`
- `tests/ui/`
- `openspec/specs/surface-grid-config-consumption/spec.md`
