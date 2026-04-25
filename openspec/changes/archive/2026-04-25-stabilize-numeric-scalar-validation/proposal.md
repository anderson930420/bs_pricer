## Why

Scalar pricing validation currently treats numeric inputs as only `int` and `float`. That rejects valid real scalar types such as `numpy.float64` and `numpy.int64`, while a naive broadened check can accidentally admit `bool`.

## What Changes

Add a centralized helper in the validation layer that recognizes finite real scalar numbers while explicitly rejecting `bool`, non-real objects, `NaN`, and infinity. Reuse that helper in the pricing validation path so domain checks continue to enforce the existing Black-Scholes policies.

## Capabilities

### New Capabilities
- `numeric-scalar-validation`: accept finite real scalar inputs from Python and numeric libraries while rejecting invalid scalar forms

## Impact

- `src/bs_pricer/validation.py`
- `tests/test_validation_policy.py`
- `openspec/specs/numeric-scalar-validation/spec.md`
