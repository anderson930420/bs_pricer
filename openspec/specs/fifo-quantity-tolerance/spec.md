# fifo-quantity-tolerance Specification

## Purpose
TBD - created by archiving change stabilize-fifo-quantity-tolerance. Update Purpose after archive.
## Requirements
### Requirement: FIFO quantity exhaustion uses a named tolerance
The FIFO matching layer MUST treat near-zero remaining quantities as exhausted using a named tolerance constant.

#### Scenario: Fractional matching closes cleanly
- **WHEN** FIFO matching consumes fractional lots whose arithmetic leaves a tiny residual quantity
- **THEN** the residual is treated as closed
- **AND** no phantom open lot remains

#### Scenario: Real inventory remains open
- **WHEN** FIFO matching leaves a meaningful nonzero remainder
- **THEN** the remainder is preserved as an open lot

#### Scenario: Tolerance is defined centrally
- **WHEN** the FIFO matching module is inspected
- **THEN** the quantity tolerance is provided by a named constant rather than an inline magic number

