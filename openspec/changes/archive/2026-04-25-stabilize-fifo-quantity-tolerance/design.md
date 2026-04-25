## Context

The portfolio FIFO layer is responsible for turning trades into open lots and realized PnL. Residual quantities created during subtraction are implementation artifacts, not meaningful inventory, so the matching layer is the right place for a narrow tolerance.

## Goals / Non-Goals

**Goals:**
- Close FIFO lots when remaining quantity is within a small tolerance of zero.
- Keep the tolerance local to portfolio matching code.
- Preserve ordinary nonzero remaining inventory.

**Non-Goals:**
- Changing pricing validation.
- Changing surface/grid code.
- Broad numeric validation changes.
- Vectorizing surface or FIFO logic.

## Decisions

- Define `QTY_EPSILON` once in the FIFO module and reuse it for exhaustion checks.
- Apply the tolerance only where FIFO matching consumes or removes residual quantities.
- Leave caller-provided quantity validation exact; only matching residuals are tolerance-aware.

## Risks / Trade-offs

- A tolerance can close very small real positions, but the threshold is intentionally narrow and only applies after arithmetic-based matching.
