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

---

## Mathematical Foundation

The project implements the standard Black-Scholes-Merton partial differential equation solutions:

$$C = S_tN(d_1) - Ke^{-rt}N(d_2)$$
$$P = Ke^{-rt}N(-d_2) - S_tN(-d_1)$$

Where $d_1$ and $d_2$ are calculated as:
$$d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$
$$d_2 = d_1 - \sigma\sqrt{T}$$

---

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

## System Specifications & Module Design

This project is built with a modular architecture, where each component has a strictly defined responsibility and technical specification.

## Module Specifications

### 1. Configuration & Input Handling
* **`config.py` (Configuration & Defaults)**:

   Centralizes default parameters and defines valid numerical ranges (min/max) for $S, K, \sigma, T, r$. It exposes constants for reuse across the CLI and Streamlit UI to avoid "magic numbers".

* **`validation.py` (Input Validation)**:

   Defines the `BSParams` data structure to hold parameters. It checks for positivity, numerical sanity (NaN/Infinity), and valid bounds to separate correctness checking from business logic.

### 2. Analytical Engine
* **`pricing.py` (Core Pricing Engine)**:

   Implements the Black-Scholes closed-form solutions. It computes $d_1, d_2$ and standard normal CDF terms to provide a unified interface for Call and Put prices.

* **`surface.py` (Option Value Surface)**:

   Generates price grids across stock prices and volatilities. It decouples batch evaluation from the core pricing engine to return matrices ready for visualization.

* **`pnl.py` (Profit & Loss Analysis)**:

   Computes P&L surfaces by accepting value surfaces and subtracting the premium element-wise. It preserves sign conventions to isolate financial interpretation from mechanics.

### 3. Data Persistence (Database Layer)
* **`db/models.py` (Database Models)**:

   Defines the persistent schema for Inputs (parameters/timestamps) and Outputs (results/shocked values) to ensure traceability.

* **`db/repo.py` (Database Access)**:

   Encapsulates database operations, including single record logging and bulk inserts for surface data. This prevents logic layers from depending on ORM details.

### 4. Interface & Quality Assurance
* **`app_streamlit.py` (Streamlit App)**:

   An interactive visualization interface that collects user input, triggers validation, and renders heatmaps.

* **`cli.py` (Command-Line Interface)**:

   A thin orchestration layer for terminal-based parameter parsing and price display with no internal business logic.

* **`tests/` (Verification)**:

   Ensures stability through pricing accuracy benchmarks, property tests (put-call parity), and database consistency checks.

## Technical Architecture Overview

The system follows a tiered architecture to deliver a professional and maintainable codebase:

| Layer | Primary Responsibility | Included Modules |
| :--- | :--- | :--- |
| **Logic** | Core Math & Validation | `pricing.py`, `validation.py` |
| **Analysis** | Grid Simulation & P&L | `surface.py`, `pnl.py` |
| **Persistence**| Data Storage & Tracking | `db/models.py`, `db/repo.py` |
| **Presentation**| CLI & Web Visualization | `cli.py`, `app_streamlit.py` |



---
*This specification is based on the project's internal function map and design documentation.*
