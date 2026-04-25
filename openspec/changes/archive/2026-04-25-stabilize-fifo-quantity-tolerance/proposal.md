## Why

FIFO matching uses repeated floating-point subtraction to consume lots. In fractional quantity workflows, that can leave tiny residual quantities that should be treated as closed but currently remain as phantom open positions.

## What Changes

Introduce a named FIFO quantity tolerance, `QTY_EPSILON = 1e-9`, in the portfolio matching layer. Use it for remaining-quantity and lot-exhaustion checks inside FIFO trade application so near-zero residuals are closed instead of preserved.

## Capabilities

### New Capabilities
- `fifo-quantity-tolerance`: tolerance-aware exhaustion of fractional FIFO lots

## Impact

- `src/bs_pricer/portfolio/pnl.py`
- `tests/portfolio/test_pnl_fifo.py`
- `openspec/specs/fifo-quantity-tolerance/spec.md`
