# Black-Scholes Pricer

A modular Black-Scholes option pricing project built with Python and Streamlit.

This project started as a learning-focused pricing engine and gradually evolved into a small analytics app with:

- Black-Scholes call/put pricing
- input validation
- option price heatmaps across spot and volatility
- FIFO PnL calculation from user-provided trades
- a clean `src/` package layout for maintainability
- a root-level Streamlit entrypoint for deployment

---

## Live Demo

[Open the Streamlit app](https://anderson930420-bs-pricer.streamlit.app/)

---

## What this project does

This app lets you interactively explore how European call and put prices change under the Black-Scholes model.

You can:

- adjust spot price, strike, volatility, time to expiry, and interest rate
- compute call and put prices from validated inputs
- visualize price surfaces as interactive heatmaps
- paste a JSON list of trades and inspect FIFO realized / unrealized PnL
- use the app in the browser through Streamlit Cloud

---

## Why I built it

I wanted this project to be more than a single pricing formula script.

My goal was to build something that reflects how I like to structure quantitative Python projects:

- separate validation from pricing logic
- keep the pricing engine small and reusable
- isolate batch surface generation from UI code
- use a package layout that can grow over time
- make the project easy to demo through a web app

So while this is still a learning-oriented project, I designed it with modularity and future extension in mind.

Last but not least, I tried to practice and push my limits while making this project.

---

## Current features

### 1. Core pricing engine
The core pricing logic computes Black-Scholes European call and put prices from the standard closed-form model.

### 2. Validation layer
Inputs are validated before pricing so that the UI and downstream logic do not need to directly handle malformed numerical inputs.

### 3. Interactive Streamlit app
The Streamlit interface provides:

- parameter sliders
- point pricing output
- heatmap controls
- FIFO PnL inputs via JSON
- interactive charts and tables

### 4. Option price heatmaps
The app generates call and put value surfaces over ranges of:

- spot price
- volatility

This makes it easier to build intuition about sensitivity to market conditions.

### 5. FIFO PnL panel
The app includes a trade-based PnL section where the user can:

- paste trade data in JSON format
- select a mark price
- compute realized PnL
- compute unrealized PnL from remaining lots
- inspect open FIFO inventory

---

## Project structure

```text
bs_pricer/
├─ src/
│  └─ bs_pricer/
│     ├─ app_streamlit.py
│     ├─ config.py
│     ├─ pricing.py
│     ├─ surface.py
│     ├─ validation.py
│     ├─ portfolio/
│     ├─ db/
│     └─ service/
├─ tests/
├─ streamlit_app.py
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

---

## What each part is responsible for

- `pricing.py`  
  Core Black-Scholes pricing logic.

- `validation.py`  
  Input checks and safe entry points before pricing.

- `surface.py`  
  Batch evaluation over spot/volatility grids for visualization.

- `app_streamlit.py`  
  Main Streamlit application logic and UI orchestration.

- `portfolio/`  
  FIFO trade and PnL-related logic.

- `db/`  
  Database-related components for persistence and traceability.

- `service/`  
  Application-level orchestration and higher-level flow.

- `streamlit_app.py`  
  Thin deployment wrapper used as the root entrypoint for Streamlit Cloud.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/anderson930420/bs_pricer.git
cd bs_pricer

```

Install dependencies:

```bash
pip install -r requirements.txt

```

## Run locally

Launch the Streamlit app from the repository root:

```bash
streamlit run streamlit_app.py

```

## How to use the app

The app supports three main workflows:

### 1. Single-option pricing
- Enter spot, strike, volatility, time to expiry, and risk-free rate to compute Black-Scholes call and put prices.

### 2. Heatmap exploration
- Adjust the spot and volatility ranges to visualize how call and put values change across different scenarios.

### 3. FIFO PnL analysis
- Paste a JSON list of trades, choose a mark price, and inspect realized PnL, unrealized PnL, net PnL, and remaining inventory.

### Example JSON for the PnL panel

In this example:

- the first two trades create a long position
- the sell trade closes the earliest open lots under FIFO
- any remaining position stays open and is valued using the selected mark price

```json
[
  {"side": "BUY", "qty": 2, "price": 10.0, "ts": "2026-01-01T09:30:00"},
  {"side": "BUY", "qty": 1, "price": 12.0, "ts": "2026-01-01T10:00:00"},
  {"side": "SELL", "qty": 2, "price": 15.0, "ts": "2026-01-02T11:00:00"}
]

```

## Testing

Run the test suite with:

```bash
pytest tests/

```

## Roadmap

Planned next steps for this project include:

- adding Greeks as first-class outputs
- supporting implied volatility calculations
- expanding automated test coverage
- improving packaging and CLI support