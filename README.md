# Black-Scholes Option Pricer - System Specifications

[cite_start]This document outlines the technical requirements, module responsibilities, and architectural rationale for the Black-Scholes Option Pricer project[cite: 2]. [cite_start]The system is designed with a focus on learning-oriented modularity and separation of concerns[cite: 3].

## Module Specifications

### 1. Configuration & Input Handling
* [cite_start]**`config.py` (Configuration & Defaults)**: Centralizes default parameters and defines valid numerical ranges (min/max) for $S, K, \sigma, T, r$[cite: 4, 5]. [cite_start]It exposes constants for reuse across the CLI and Streamlit UI to avoid "magic numbers"[cite: 8, 9].
* [cite_start]**`validation.py` (Input Validation)**: Defines the `BSParams` data structure to hold parameters[cite: 11, 12]. [cite_start]It checks for positivity, numerical sanity (NaN/Infinity), and valid bounds to separate correctness checking from business logic[cite: 13, 15].

### 2. Analytical Engine
* [cite_start]**`pricing.py` (Core Pricing Engine)**: Implements the Black-Scholes closed-form solutions[cite: 16, 18]. [cite_start]It computes $d_1, d_2$ and standard normal CDF terms to provide a unified interface for Call and Put prices[cite: 19, 21, 22].
* [cite_start]**`surface.py` (Option Value Surface)**: Generates price grids across stock prices and volatilities[cite: 24, 25]. [cite_start]It decouples batch evaluation from the core pricing engine to return matrices ready for visualization[cite: 28, 30].
* [cite_start]**`pnl.py` (Profit & Loss Analysis)**: Computes P&L surfaces by accepting value surfaces and subtracting the premium element-wise[cite: 31, 33, 34, 35]. [cite_start]It preserves sign conventions to isolate financial interpretation from mechanics[cite: 36, 37].

### 3. Data Persistence (Database Layer)
* [cite_start]**`db/models.py` (Database Models)**: Defines the persistent schema for Inputs (parameters/timestamps) and Outputs (results/shocked values) to ensure traceability[cite: 38, 40, 41, 42, 43].
* [cite_start]**`db/repo.py` (Database Access)**: Encapsulates database operations, including single record logging and bulk inserts for surface data[cite: 44, 45, 46, 47]. [cite_start]This prevents logic layers from depending on ORM details[cite: 49].

### 4. Interface & Quality Assurance
* [cite_start]**`app_streamlit.py` (Streamlit App)**: An interactive visualization interface that collects user input, triggers validation, and renders heatmaps[cite: 59, 61, 62, 63, 64].
* **`cli.py` (Command-Line Interface)**: A thin orchestration layer for terminal-based parameter parsing and price display with no internal business logic[cite: 50, 52, 53, 58].
* [cite_start]**`tests/` (Verification)**: Ensures stability through pricing accuracy benchmarks, property tests (put-call parity), and database consistency checks[cite: 67, 68, 69, 70, 72].

## Technical Architecture Overview

[cite_start]The system follows a tiered architecture to deliver a professional and maintainable codebase[cite: 75, 80]:

| Layer | Primary Responsibility | Included Modules |
| :--- | :--- | :--- |
| **Logic** | Core Math & Validation | `pricing.py`, `validation.py` |
| **Analysis** | Grid Simulation & P&L | `surface.py`, `pnl.py` |
| **Persistence**| Data Storage & Tracking | `db/models.py`, `db/repo.py` |
| **Presentation**| CLI & Web Visualization | `cli.py`, `app_streamlit.py` |



---
[cite_start]*This specification is based on the [Black-Scholes Function Map](Black_Scholes_Function_Map_Formatted.pdf)[cite: 1].*