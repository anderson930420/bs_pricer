from bs_pricer import pricing
import math
# validation.py (module level)

def _validate_numbers(S, K, sigma, T, r):
    # 檢查 type + NaN/inf（重點：NaN/inf）
    if not isinstance(S, (int, float)):
        raise TypeError("S must be a number")
    if not isinstance(K, (int, float)):
        raise TypeError("K must be a number")
    if not isinstance(sigma, (int, float)):
        raise TypeError("sigma must be a number")
    if not isinstance(T, (int, float)):
        raise TypeError("T must be a number")
    if not isinstance(r, (int, float)):
        raise TypeError("r must be a number")

    if not math.isfinite(S):
        raise ValueError("S is not finite")
    if not math.isfinite(K):
        raise ValueError("K is not finite")
    if not math.isfinite(sigma):
        raise ValueError("sigma is not finite")
    if not math.isfinite(T):
        raise ValueError("T is not finite")
    if not math.isfinite(r):
        raise ValueError("r is not finite")

def _validate_domain(S, K, sigma, T, r):
    # S > 0, K > 0
    # T >= 0, sigma >= 0
    # r 不限制正負
    if  S <= 0:
        raise ValueError("S must > 0")
    if not K > 0:
        raise ValueError("K must > 0")
    if not sigma >= 0:
        raise ValueError("sigma must be non-negative")
    if not T >= 0:
        raise ValueError("T must be non-negative")

def _payoff_at_expiry(S, K):
    # 回 {"call": ..., "put": ...}
    call_price = max(0.0, S - K)
    put_price = max(0.0, K - S)
    return {"call": call_price, "put": put_price}

def _deterministic_limit_sigma_zero(S, K, T, r):
    # σ=0, T>0 的 policy
    # 回 {"call": ..., "put": ...}
    pv_k = K * math.exp(-r*T)
    expected_call = max(S - pv_k, 0)
    expected_put = max(pv_k - S, 0)
    return {"call": expected_call, "put": expected_put}

def price_checked(S, K, sigma, T, r):
    _validate_numbers(S, K, sigma, T, r)
    _validate_domain(S, K, sigma, T, r)

    if T == 0:
        return _payoff_at_expiry(S, K)

    elif sigma == 0:
        return _deterministic_limit_sigma_zero(S, K, T, r)

    # normal path
    return pricing.price(S, K, sigma, T, r)
