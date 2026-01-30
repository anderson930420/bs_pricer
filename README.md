# Black-Scholes Option Pricer

A professional Python implementation of the Black-Scholes model for European option pricing, Greek risk analysis, and dynamic P&L visualization.

## Features

* **Core Pricing Engine**: Exact closed-form solutions for European Call and Put options.
* **The Greeks**: Real-time calculation of Delta, Gamma, Theta, Vega, and Rho.
* **Interactive Dashboard**: Streamlit-based web interface with real-time parameter tuning.
* **Heatmap Visualization**: 2D surface analysis for Option Value and P&L across varying Spot Prices and Volatilities.
* **Persistence Layer**: Built-in database support for calculation traceability and historical logging.

## Project Structure

The project follows a modular architecture based on the Separation of Concerns (SoC) principle:

| Module | Description |
| :--- | :--- |
| `pricing.py` | Core mathematical engine for $d_1$, $d_2$, and BS formulas. |
| `surface.py` | Grid generation for batch evaluation of option surfaces. |
| `pnl.py` | Profit & Loss logic for translating value surfaces into net P&L. |
| `validation.py` | Input sanitization and bounds checking for (S, K, σ, T, r). |
| `db/` | Database models and repository layer for data persistence. |
| `app_streamlit.py` | Interactive UI and visualization orchestration. |

## Getting Started

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/anderson930420/bs_pricer.git](https://github.com/anderson930420/bs_pricer.git)
   cd bs_pricer
   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt 
   ```
## Usage

### Launch Web Interface
   ```bash
   streamlit run app_streamlit.pybash
   ```

### Command-Line Interface (CLI):
   ```bash
   python cli.py --S 100 --K 100 --T 1 --r 0.05 --sigma 0.2
   ```

## Testing

A comprehensive test suite is included to ensure numerical precision:

* **Benchmark pricing accuracy.**

* **Property tests (Non-negativity, Put-Call Parity).**

* **Surface data consistency checks.**
  
Run tests via:
   ```bash
  pytest tests/
  ```
