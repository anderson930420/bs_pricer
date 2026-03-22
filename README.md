# Black-Scholes Pricer

A small, modular Black-Scholes pricing project built with Python and Streamlit.

It combines a validated pricing engine, interactive heatmaps, and FIFO trade-based PnL tooling in a `src/`-layout codebase that is easy to run locally and straightforward to extend.

## Overview

This repository models European call and put option prices with the Black-Scholes formula and exposes that logic through:

- a Streamlit app for interactive exploration
- a reusable Python package under `src/bs_pricer`
- a lightweight CLI entrypoint
- automated tests for pricing, validation, surface generation, persistence, and UI import smoke coverage

The app is designed for quick intuition-building:

- inspect single-point call and put prices
- explore option value heatmaps across spot price and volatility
- switch heatmaps between Price and PnL views
- evaluate FIFO realized and unrealized PnL from user-provided JSON trades

## Live Demo

[Open the Streamlit app](https://anderson930420-bs-pricer.streamlit.app/)

## Features

- Black-Scholes European call and put pricing
- validated pricing inputs before downstream computation
- interactive Streamlit UI for pricing and scenario exploration
- option value surfaces over spot price and volatility
- Price / PnL heatmap toggle
- PnL heatmaps derived directly from the option value surface
- long / short position handling in PnL mode
- intuitive heatmap color semantics:
  - Price mode: Call = blue sequential scale, Put = orange sequential scale
  - PnL mode: red = loss, neutral = near break-even, green = profit
- FIFO trade-based PnL panel from JSON input
- `src/` package layout for cleaner separation of UI, pricing, portfolio, and persistence logic
- root-level Streamlit deployment entrypoint via `streamlit_app.py`

## Heatmap Modes

The heatmap section uses the same spot-price and volatility grid in both modes.

### Price mode

Price mode shows option value magnitude only:

- Call heatmap uses a blue sequential palette
- Put heatmap uses an orange sequential palette
- deeper color means higher option price

### PnL mode

PnL mode reuses the same value surface and applies:

```text
PnL = (current option value - entry price) * quantity
```

with position direction applied as:

- `Long` = positive exposure to price changes
- `Short` = sign-inverted PnL

The PnL heatmaps use a zero-centered diverging colorscale:

- red for losses
- neutral near break-even
- green for profits

## App Workflows

### 1. Single-option pricing

Use the sidebar inputs to price one European call and one European put at the current parameter set:

- Spot price
- Strike price
- Time to maturity
- Volatility
- Risk-free rate

### 2. Heatmap exploration

Adjust the heatmap grid to evaluate option values or PnL across:

- spot price range
- volatility range
- grid density

This is useful for comparing how call and put behavior changes under different scenarios while keeping strike, rate, and maturity fixed.

### 3. FIFO PnL panel

Paste a JSON list of trades into the Streamlit app to inspect:

- realized PnL
- unrealized PnL
- total net PnL
- remaining FIFO lots

The panel supports selectable mark pricing using the current call value, current put value, or a custom mark.

## FIFO PnL Panel

The FIFO section is separate from the heatmap PnL view.

- Heatmap PnL is scenario-based and derived from the option value surface.
- FIFO PnL is trade-based and derived from the JSON trade list plus a chosen mark price.

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

## Project Structure

```text
bs_pricer/
├─ src/
│  └─ bs_pricer/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ app_streamlit.py
│     ├─ config.py
│     ├─ pricing.py
│     ├─ surface.py
│     ├─ validation.py
│     ├─ db/
│     ├─ portfolio/
│     └─ service/
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

### Key files

- `src/bs_pricer/pricing.py`
  Black-Scholes pricing logic.
- `src/bs_pricer/validation.py`
  Input validation and safe pricing entrypoints.
- `src/bs_pricer/surface.py`
  Value-surface generation across spot/volatility grids.
- `src/bs_pricer/app_streamlit.py`
  Main Streamlit app UI and heatmap logic.
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

## Run Locally

Launch the Streamlit app from the repository root:

```bash
streamlit run streamlit_app.py
```

The deployed app entrypoint is the same root file:

```text
streamlit_app.py
```

There is also a package CLI entrypoint:

```bash
python -m bs_pricer price --S 100 --K 100 --sigma 0.2 --T 1.0 --r 0.05 --no-persist
```

## Testing

Run the full test suite from the repository root:

```bash
pytest
```

The test suite currently covers:

- pricing behavior
- validation policy
- value surface generation
- FIFO portfolio logic
- SQLite repository behavior
- pricing service flows
- CLI smoke tests
- Streamlit app import smoke test

## Why This Project

This project is a compact way to show a few engineering habits in one place:

- separating core pricing logic from UI concerns
- validating inputs at the application boundary
- reusing the same value surface for multiple visual workflows
- keeping the code organized under a maintainable `src/` layout
- pairing quantitative logic with a practical interface

## Roadmap

Potential next steps for the project:

- Greeks as first-class outputs in the UI and CLI
- implied volatility calculations
- richer historical run exploration on top of the SQLite layer
- more targeted UI and visualization tests
- packaging and release polish
