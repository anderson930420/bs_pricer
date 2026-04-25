"""Black-Scholes analytic Greeks for scalar call and put options."""

from __future__ import annotations

from dataclasses import dataclass
import math

from ._bs_core import d1_d2, norm_cdf, norm_pdf


@dataclass(frozen=True)
class GreekValues:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float


@dataclass(frozen=True)
class Greeks:
    call: GreekValues
    put: GreekValues


def greeks(S: float, K: float, sigma: float, T: float, r: float) -> Greeks:
    """Compute Black-Scholes Greeks for call and put options.

    Unit conventions:
    - delta is dV/dS.
    - gamma is d2V/dS2.
    - vega is dV/dsigma where sigma is decimal volatility, e.g. 0.20.
    - theta is market-convention theta, -dV/dT, where T is time to expiry.
      It represents value change as calendar time passes, holding other inputs
      constant.
    - rho is dV/dr where r is a decimal rate, e.g. 0.05.

    This analytic function assumes T > 0 and sigma > 0. Use the checked
    validation-layer API for public input validation.
    """
    d1, d2 = d1_d2(S, K, T, r, sigma)
    n_d1 = norm_cdf(d1)
    n_d2 = norm_cdf(d2)
    pdf_d1 = norm_pdf(d1)
    sqrt_t = math.sqrt(T)
    discounted_factor = math.exp(-r * T)

    call_delta = n_d1
    put_delta = n_d1 - 1.0
    gamma = pdf_d1 / (S * sigma * sqrt_t)
    vega = S * pdf_d1 * sqrt_t
    shared_theta_decay = -S * pdf_d1 * sigma / (2.0 * sqrt_t)
    call_theta = shared_theta_decay - r * K * discounted_factor * n_d2
    put_theta = shared_theta_decay + r * K * discounted_factor * norm_cdf(-d2)
    call_rho = K * T * discounted_factor * n_d2
    put_rho = -K * T * discounted_factor * norm_cdf(-d2)

    return Greeks(
        call=GreekValues(
            delta=call_delta,
            gamma=gamma,
            vega=vega,
            theta=call_theta,
            rho=call_rho,
        ),
        put=GreekValues(
            delta=put_delta,
            gamma=gamma,
            vega=vega,
            theta=put_theta,
            rho=put_rho,
        ),
    )
