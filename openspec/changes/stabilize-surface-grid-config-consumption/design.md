## Context

`config.py` owns the canonical grid settings for surface analysis. The Streamlit app currently bypasses that contract by reading legacy key names that no longer exist. Surface generation itself is already correct when given explicit `S_axis` and `sigma_axis` values.

## Goals / Non-Goals

**Goals:**
- Consume canonical `GRID_CONFIG` keys in the app boundary.
- Keep `surface.py` focused on explicit-axis surface computation.
- Avoid direct stale-key interpretation in the Streamlit UI.
- Add regression tests for the config-to-defaults conversion path.

**Non-Goals:**
- Changing the surface calculation contract.
- Adding FIFO tolerance handling.
- Adding scalar validation changes.
- Introducing vectorized surface evaluation.

## Decisions

- Add a tiny helper module at the app boundary to translate canonical grid config into concrete defaults.
- Keep `surface.py` free of `config.py` imports so the surface layer stays explicit and reusable.
- Keep the UI change minimal: only the grid-default path changes, not the downstream surface math.

## Risks / Trade-offs

- The helper introduces one more boundary module, but it isolates the config contract and prevents stale-key drift.
- Spot-axis defaults are derived from the current spot value, so the UI defaults move with the selected input rather than from a hardcoded absolute range.
