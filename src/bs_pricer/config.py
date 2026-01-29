# NOTE: These constraints are for UI guidance only.
# Domain validity is enforced by validation.py, not here.
"""
Shared Configuration Layer

Responsibility:
    - Define default values for the pricing model.
    - Define UI constraints (min, max, step) for CLI and Streamlit.
    - Define grid settings for surface analysis.

Constraints:
    - Pure data only.
    - No business logic or conditional statements.
    - No dependencies on core modules (pricing, validation).
"""

from typing import Dict, Any

# 1. Default Parameter Values
# Single Source of Truth for: CLI defaults, Streamlit initialization, and Unit Tests.
DEFAULT_PARAMS: Dict[str, float] = {
    "S": 100.0,   # Spot Price
    "K": 100.0,   # Strike Price
    "T": 1.0,     # Time to Maturity (Years)
    "r": 0.05,    # Risk-free Rate (5%)
    "sigma": 0.2, # Volatility (20%)
}

# 2. UI & Input Constraints
# Metadata for frontend components (Streamlit sliders, CLI help messages).
# Structure: { parameter_name: { min, max, step, label, help } }
UI_CONFIG: Dict[str, Dict[str, Any]] = {
    "S": {
        "min": 1.0,
        "max": 500.0,
        "step": 1.0,
        "label": "Spot Price (S)",
        "help": "Current price of the underlying asset."
    },
    "K": {
        "min": 1.0,
        "max": 500.0,
        "step": 1.0,
        "label": "Strike Price (K)",
        "help": "Strike price of the option."
    },
    "T": {
        "min": 0.0,   # T=0 is allowed and handled by validation/pricing policies
        "max": 10.0,
        "step": 0.1,
        "label": "Time to Maturity (T)",
        "help": "Time to expiration in years."
    },
    "r": {
        "min": 0.0,
        "max": 0.20,  # Cap at 20% for realistic bounds
        "step": 0.01,
        "label": "Risk-Free Rate (r)",
        "help": "Annualized risk-free interest rate (decimal)."
    },
    "sigma": {
        "min": 0.0,   # Sigma=0 is allowed (deterministic limit)
        "max": 2.0,   # 200% Volatility
        "step": 0.05,
        "label": "Volatility (σ)",
        "help": "Annualized standard deviation of returns (decimal)."
    }
}

# 3. Surface Analysis Grid Settings
# Controls the range and density of the mesh grid generation.
GRID_CONFIG: Dict[str, Any] = {
    "SPOT_MIN_PCT": 0.5,  # Start grid at 50% of Spot Price
    "SPOT_MAX_PCT": 1.5,  # End grid at 150% of Spot Price
    "SPOT_STEPS": 50,     # Number of steps for Spot axis

    "VOL_MIN": 0.05,      # Minimum volatility in grid
    "VOL_MAX": 0.50,      # Maximum volatility in grid
    "VOL_STEPS": 20,      # Number of steps for Volatility axis
}