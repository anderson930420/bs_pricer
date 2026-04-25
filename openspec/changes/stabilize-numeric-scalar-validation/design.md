## Context

The validation layer is the right place to normalize scalar input acceptance. Pricing math should remain numeric and domain-agnostic, while validation handles caller-facing type and finiteness policy.

## Goals / Non-Goals

**Goals:**
- Accept finite real scalar numeric inputs from Python and numpy.
- Reject `bool` even though it is a `numbers.Real` subclass.
- Reject strings, NaN, infinity, and other non-real inputs.
- Preserve existing domain rules and expiry / deterministic-limit policies.

**Non-Goals:**
- Changing Black-Scholes pricing formulas.
- Broadening validation to vectorized inputs.
- Changing surface/grid code.
- Changing portfolio/FIFO code.

## Decisions

- Add `_is_finite_real_number(value: object) -> bool` in `validation.py`.
- Make the helper reject `bool` first, then require `numbers.Real`, then check finiteness via `math.isfinite(float(value))`.
- Keep the helper local to scalar validation so the rest of the project does not depend on it.

## Risks / Trade-offs

- Using `numbers.Real` is broader than the old `int`/`float` check, but the explicit `bool` rejection and finiteness check keep the acceptance set controlled.
