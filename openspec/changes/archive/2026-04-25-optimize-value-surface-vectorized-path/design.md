## Context

`value_surface(...)` is the canonical correctness path. It accepts an injected scalar engine, which is important for testability and alternative pricing engines, but it is not optimized for bulk grid evaluation.

## Goals / Non-Goals

**Goals:**
- Add a separate vectorized NumPy fast path for explicit-axis surface generation.
- Preserve `value_surface(...)` exactly as the canonical scalar path.
- Preserve financial edge policies for expiry and sigma-zero cases.
- Keep `surface.py` explicit-axis only and free of config dependencies.

**Non-Goals:**
- Rewriting or removing the scalar engine-injected path.
- Changing validation policy.
- Changing surface-grid config translation.
- Changing portfolio/FIFO logic.
- Adding UI or CLI changes beyond what is strictly necessary.

## Decisions

- Implement `value_surface_fast(...)` as a separate function in `surface.py`.
- Use explicit branch and mask assignment rather than `np.where` for edge handling.
- Use SciPy's vectorized normal CDF support to keep the fast path compact and performant.
- Keep the fast path engine-free so it is not coupled to scalar injection or validation.

## Risks / Trade-offs

- The fast path duplicates some surface formula logic, but only in the performance-oriented function.
- Keeping both APIs side by side means callers must choose the correct path for their needs.
