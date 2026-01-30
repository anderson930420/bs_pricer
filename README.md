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

## System Specifications & Module Design

This project is built with a modular architecture, where each component has a strictly defined responsibility and technical specification.

### 1. Configuration & Input Handling
* [cite_start]**`config.py` (Configuration)**: Centralizes default parameters and valid numerical ranges for $S, K, \sigma, T, r$[cite: 4, 5]. [cite_start]It defines min/max bounds for validation and UI sliders to ensure consistent constraints across the project[cite: 7, 9].
* [cite_start]**`validation.py` (Input Validation)**: Defines the `BSParams` data structure to hold core parameters[cite: 10, 12]. [cite_start]It performs positivity checks and numerical sanity tests (NaN/Infinity) before raising user-facing errors[cite: 13, 14].

### 2. Analytical Engine
* [cite_start]**`pricing.py` (Core Engine)**: Implements the Black-Scholes closed-form pricing logic[cite: 16, 18]. [cite_start]It computes $d_1$, $d_2$, and the standard normal CDF to provide a unified interface for both Call and Put prices[cite: 19, 21, 22].
* [cite_start]**`surface.py` (Option Value Surface)**: Generates a 2D grid across stock prices and volatilities[cite: 24, 25]. [cite_start]It decouples batch evaluation from the core pricing logic to return a value matrix for visualization[cite: 28, 30].
* [cite_start]**`pnl.py` (Profit & Loss Analysis)**: Accepts the option value surface and subtracts the premium element-wise to compute P&L[cite: 31, 33, 35]. [cite_start]It preserves sign conventions to isolate financial interpretation from pricing mechanics[cite: 36, 37].

### 3. Data Persistence & Infrastructure
* [cite_start]**`db/models.py` (Database Models)**: Defines the persistent schema for Inputs (parameters/timestamps) and Outputs (results/shocked values) to ensure reproducibility[cite: 38, 40, 41, 43].
* [cite_start]**`db/repo.py` (Repository Layer)**: Encapsulates database operations, including single record inserts and bulk inserts for surface results[cite: 44, 45, 47]. [cite_start]This prevents the UI from depending on ORM details[cite: 49].

### 4. Interface & Quality Assurance
* [cite_start]**`app_streamlit.py` (Web UI)**: Collects user inputs via widgets, triggers validation, and renders interactive heatmaps[cite: 59, 62, 64]. [cite_start]It is designed so the UI only orchestrates and visualizes, never computes[cite: 66].
* [cite_start]**`cli.py` (CLI Interface)**: A thin orchestration layer for terminal-based parameter parsing, price computation, and data persistence[cite: 50, 53, 58].
* [cite_start]**`tests/` (Verification)**: Ensures stability through pricing accuracy benchmarks, property tests (put-call parity), and database consistency checks[cite: 67, 69, 70, 72].

## Technical Architecture Overview

| Layer | Responsibility | Key Modules |
| :--- | :--- | :--- |
| **Logic** | Pricing & Greeks calculation | `pricing.py`, `validation.py` |
| **Analysis** | Grid evaluation & P&L mapping | `surface.py`, `pnl.py` |
| **Storage** | Persistence & traceability | `db/models.py`, `db/repo.py` |
| **UI** | Visualization & interaction | `app_streamlit.py`, `cli.py` |

---
[cite_start]*Specifications are based on the project's internal Function Map & Design Document[cite: 1, 2].*
