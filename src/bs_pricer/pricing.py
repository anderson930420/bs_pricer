"""Only pricing functions for the Black-Scholes-Merton model.

No validation, IO, or UI formatting belongs here.
"""

import math

from ._bs_core import d1_d2, norm_cdf


def _d1_d2(S, K, sigma, T, r):
    # Compatibility wrapper for existing imports that use the old private order.
    return d1_d2(S, K, T, r, sigma)


def _norm_cdf(x: float) -> float:
    """
    Standard normal cumulative distribution function N(x).
    """
    return norm_cdf(x)


def price(S, K, sigma, T, r):
    """Return Black-Scholes call and put prices."""
    d1, d2 = d1_d2(S, K, T, r, sigma)
    n_d1 = norm_cdf(d1)
    n_d2 = norm_cdf(d2)
    call_price = S * n_d1 - K * math.exp(-r * T) * n_d2
    put_price = K * math.exp(-r * T) * (1 - n_d2) - S * (1 - n_d1)
    return {"call": call_price, "put": put_price}
