## 1. FIFO Matching Update

- [x] 1.1 Add a named FIFO quantity tolerance constant in the portfolio matching module.
- [x] 1.2 Use the tolerance in remaining-quantity and lot-exhaustion checks.

## 2. Regression Coverage

- [x] 2.1 Add a test showing fractional trades that should fully close do not leave phantom lots.
- [x] 2.2 Add a test showing legitimate nonzero remaining inventory is preserved.
- [x] 2.3 Add a test proving the tolerance is referenced through the named constant rather than an inline magic number.
