# Black-Scholes Pricer

A modular Black-Scholes single-option risk analysis app built with Python and Streamlit.

The project combines validated European call/put pricing, analytic Greeks, selected-option scenario analysis, first-order Greek price bridge decomposition, option value surfaces, and FIFO trade-based PnL tooling in a `src/`-layout codebase.

## Overview

This repository exposes the option model through:

- a Streamlit app for interactive price, Greeks, scenario, surface, and FIFO PnL workflows
- a reusable Python package under `src/bs_pricer`
- a lightweight CLI entrypoint
- automated tests for pricing, validation, Greeks, scenarios, surfaces, persistence, portfolio PnL, CLI behavior, and UI import smoke coverage

The app is designed for quick single-option risk intuition:

- inspect call and put prices
- inspect Black-Scholes Greeks with market conventions
- analyze a selected long call or long put under preset scenarios
- decompose scenario repricing into delta, vega, theta, rho, first-order approximation, and residual
- explore option value and PnL heatmaps across spot price and volatility
- evaluate FIFO realized and unrealized PnL from user-provided JSON trades

## Live Demo

[Open the Streamlit app](https://anderson930420-bs-pricer.streamlit.app/)

## Features

- Black-Scholes European call and put pricing
- validated pricing inputs before downstream computation
- Black-Scholes Greeks as first-class outputs:
  - delta
  - gamma
  - vega
  - market-convention theta
  - rho
- UI conversions for risk units:
  - daily theta is displayed as `theta / 365`
  - vega is displayed per volatility point as `vega * 0.01`
  - rho is displayed per rate point as `rho * 0.01`
- selected-option scenario analysis for long call or long put
- scenario presets for spot, volatility, time, and rate shifts
- first-order Greek price bridge decomposition:
  - delta effect
  - vega effect
  - theta effect
  - rho effect
  - first-order approximation
  - residual repricing effect
- option value surfaces over spot price and volatility
- Price / PnL heatmap toggle
- PnL heatmaps derived directly from the option value surface
- long / short position handling in PnL mode
- FIFO trade-based PnL panel from JSON input
- `src/` package layout for separation of scalar math, pricing, validation, Greeks, scenarios, surfaces, UI, portfolio, and persistence logic
- root-level Streamlit deployment entrypoint via `streamlit_app.py`

## App Usage

Launch the app from the repository root:

```bash
streamlit run streamlit_app.py
```

The sidebar controls the base option inputs:

- spot price
- strike price
- time to maturity
- volatility
- risk-free rate
- selected option type for scenario analysis
- surface grid settings
- heatmap mode settings

### Price & Greeks Tab

The Price & Greeks tab shows current call and put prices plus call/put Greek values.

Greeks use these conventions:

- delta is `dV/dS`
- gamma is `d2V/dS2`
- vega is `dV/dsigma`, where volatility is a decimal such as `0.20`
- theta is market-convention theta, `-dV/dT`
- rho is `dV/dr`, where rate is a decimal such as `0.05`

The UI also shows daily theta, vega per volatility point, and rho per rate point. If time to expiry is zero or volatility is zero, prices remain available but analytic Greeks are shown as unavailable.

### Scenario Analysis Tab

The Scenario Analysis tab follows the selected option type from the sidebar and clearly displays the analyzed option, such as `Long Call` or `Long Put`.

For each preset scenario, the tab shows:

- base price
- changed inputs with before and after values
- scenario price
- actual repricing change
- first-order approximate change
- bridge table with delta, vega, theta, rho, first-order approximation, actual repricing change, and residual

The bridge uses base-case Greeks. Vega and rho shifts are converted from points to decimal units before applying the bridge. The residual captures the portion of repricing not explained by first-order Greeks, including nonlinear effects such as gamma.

### Surfaces Tab

The Surfaces tab renders call and put heatmaps across a spot/volatility grid.

Price mode shows option value magnitude:

- call heatmap uses a blue sequential palette
- put heatmap uses an orange sequential palette

PnL mode reuses the same value surface and applies:

```text
PnL = (current option value - entry price) * quantity
```

with position direction applied as:

- `Long` = positive exposure to price changes
- `Short` = sign-inverted PnL

### FIFO PnL Workflow

The FIFO PnL workflow is available in the Surfaces tab. Paste a JSON list of trades to inspect:

- realized PnL
- unrealized PnL
- total net PnL
- remaining FIFO lots

The mark price can be the current call value, current put value, or a custom mark.

Example JSON input:

```json
[
  {
    "instrument_id": "AAPL",
    "ts_utc": "2026-01-01T00:00:00Z",
    "side": "BUY",
    "qty": 1.0,
    "price": 90.0,
    "fees": 0.0
  },
  {
    "instrument_id": "AAPL",
    "ts_utc": "2026-01-02T00:00:00Z",
    "side": "SELL",
    "qty": 0.5,
    "price": 95.0,
    "fees": 0.0
  }
]
```

## CLI Usage

Run the default price command with configured defaults:

```bash
python3 -m bs_pricer
```

Run an explicit price calculation:

```bash
python3 -m bs_pricer price --S 100 --K 100 --sigma 0.2 --T 1.0 --r 0.05 --no-persist
```

Persist a pricing run to SQLite:

```bash
python3 -m bs_pricer price --persist --db bs_pricer.sqlite3
```

List recent persisted runs:

```bash
python3 -m bs_pricer history --db bs_pricer.sqlite3 --limit 10
```

Show a persisted run:

```bash
python3 -m bs_pricer show --db bs_pricer.sqlite3 --run-id <run_id>
```

Show help:

```bash
python3 -m bs_pricer --help
python3 -m bs_pricer price --help
```

## Project Structure

```text
bs_pricer/
├─ bs_pricer/
│  └─ __init__.py
├─ src/
│  └─ bs_pricer/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ _bs_core.py
│     ├─ app_streamlit.py
│     ├─ config.py
│     ├─ greeks.py
│     ├─ pricing.py
│     ├─ scenario.py
│     ├─ surface.py
│     ├─ surface_grid.py
│     ├─ validation.py
│     ├─ db/
│     ├─ portfolio/
│     └─ service/
├─ openspec/
├─ tests/
│  ├─ cli/
│  ├─ db/
│  ├─ portfolio/
│  ├─ service/
│  └─ ui/
├─ streamlit_app.py
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

### Key Files

- `src/bs_pricer/_bs_core.py`
  Scalar Black-Scholes math helpers for normal CDF/PDF and d1/d2.
- `src/bs_pricer/pricing.py`
  Black-Scholes scalar pricing logic.
- `src/bs_pricer/greeks.py`
  Black-Scholes analytic Greeks and Greek dataclasses.
- `src/bs_pricer/scenario.py`
  Scenario presets, input shifting, selected-option repricing, first-order bridge, and residual logic.
- `src/bs_pricer/validation.py`
  Input validation, safe pricing entrypoint, and checked Greeks entrypoint.
- `src/bs_pricer/surface.py`
  Value-surface generation across spot/volatility grids.
- `src/bs_pricer/app_streamlit.py`
  Streamlit tabs and UI rendering.
- `src/bs_pricer/__main__.py`
  CLI parser and command dispatch for price/history/show.
- `src/bs_pricer/portfolio/`
  FIFO inventory and PnL logic.
- `src/bs_pricer/db/`
  SQLite persistence models and repository code.
- `src/bs_pricer/service/`
  Higher-level service orchestration for pricing and replay flows.
- `streamlit_app.py`
  Root Streamlit entrypoint used for deployment.

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/anderson930420/bs_pricer.git
cd bs_pricer
pip install -r requirements.txt
```

## Testing

Run the full test suite from the repository root:

```bash
python3 -m pytest
```

The test suite covers:

- scalar core helpers
- pricing behavior
- validation policy
- Greeks conventions and checked API behavior
- scenario transformations and bridge decomposition
- value surface generation
- FIFO portfolio logic
- SQLite repository behavior
- pricing service flows
- CLI smoke tests
- Streamlit app import smoke test

## Why This Project

This project is a compact way to show a few engineering habits in one place:

- separating scalar math and domain logic from UI concerns
- validating inputs at the application boundary
- documenting risk unit conventions explicitly
- reusing the same value surface for multiple visual workflows
- keeping the code organized under a maintainable `src/` layout
- pairing quantitative logic with a practical interface

## Roadmap

Potential next steps for the project:

- implied volatility calculations
- richer historical run exploration on top of the SQLite layer
- custom user-defined scenario presets
- more targeted UI and visualization tests
- packaging and release polish
