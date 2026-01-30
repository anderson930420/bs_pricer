# bs_pricer — Black–Scholes Pricing Engine 

A layered Black–Scholes pricing system with strict validation, surface generation,
FIFO PnL calculation, and a Streamlit UI as a pure consumer.

This project emphasizes **clear responsibility boundaries**, **test-backed correctness**,
and **reproducibility** over feature count.

---

## Features (Current)
- Black–Scholes call / put pricing (pure core)
- Centralized validation policy (`price_checked`)
- Value surface generation (S × σ grid) with invariants
- SQLite persistence for pricing runs (persist + replay)
- FIFO PnL core (pure calculation, no IO)
- Streamlit UI:
  - Point pricing
  - Heatmaps
  - FIFO PnL with selectable mark (CALL / PUT / Custom)

---

## Project Structure (src-layout)

