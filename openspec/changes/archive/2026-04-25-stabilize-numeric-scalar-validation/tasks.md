## 1. Validation Helper

- [x] 1.1 Add `_is_finite_real_number(value: object) -> bool` to the validation layer.
- [x] 1.2 Update scalar validation to use the helper for each pricing input.

## 2. Regression Coverage

- [x] 2.1 Add tests accepting `numpy.float64` and `numpy.int64` when domain-valid.
- [x] 2.2 Add tests rejecting `bool`, NaN, infinity, strings, and non-real objects.
- [x] 2.3 Add tests preserving `T = 0` payoff policy and `sigma = 0` deterministic-limit policy.
