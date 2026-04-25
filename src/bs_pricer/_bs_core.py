"""Scalar Black-Scholes math helpers.

This module intentionally owns only scalar mathematical primitives. Validation,
scenario logic, UI formatting, and vectorized surface generation live elsewhere.
"""

from __future__ import annotations

import math

from scipy.special import ndtr


def norm_cdf(x: float) -> float:
    """Standard normal CDF N(x)."""
    return float(ndtr(float(x)))


def norm_pdf(x: float) -> float:
    """Standard normal PDF: phi(x) = exp(-x^2/2) / sqrt(2*pi)."""
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def d1_d2(S: float, K: float, T: float, r: float, sigma: float) -> tuple[float, float]:
    vol_sqrt_t = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t
    return d1, d2
