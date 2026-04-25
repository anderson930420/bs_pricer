## 1. Fast Path Implementation

- [x] 1.1 Add `value_surface_fast(...)` to `src/bs_pricer/surface.py` as a separate vectorized NumPy implementation.
- [x] 1.2 Preserve the existing scalar `value_surface(...)` engine-injected path unchanged.

## 2. Regression Coverage

- [x] 2.1 Add tests for shape and axis ordering parity with the scalar path.
- [x] 2.2 Add numerical equivalence tests at selected grid points.
- [x] 2.3 Add edge-case tests for `T = 0` and `sigma = 0`.
- [x] 2.4 Add tests for put-call parity, engine injection preservation, and boundary checks.
