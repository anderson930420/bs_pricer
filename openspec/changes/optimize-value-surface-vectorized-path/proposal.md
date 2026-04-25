## Why

The project already has a canonical scalar surface builder that is correct and engine-injected, but it evaluates each grid cell one at a time. A separate vectorized path can speed up visualization and bulk surface generation without changing the existing correctness-oriented API.

## What Changes

Add a new vectorized NumPy surface generator alongside the existing scalar `value_surface(...)` function. The new API will compute the same call/put value surface from explicit axes, but it will use vectorized Black-Scholes math and no engine injection.

## Capabilities

### New Capabilities
- `value-surface-fast-path`: fast vectorized value surface generation for explicit axes

## Impact

- `src/bs_pricer/surface.py`
- `tests/test_surface.py`
- `openspec/specs/value-surface-fast-path/spec.md`
