'''Only Pricing function for Black-Scholes-Merton model
    No validation / IO / formatting'''
import math
def _d1_d2(S, K, sigma, T, r):
        raise NotImplementedError

def _norm_cdf(x: float) -> float:
    """
    Standard normal cumulative distribution function N(x).
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def price(S, K, sigma, T, r):
    '''
    Docstring for price
    :param S: Price of the underlying asset at time t
    :param K: Strike price of the option
    :param sigma: Volatility (annualized standard deviation of returns)
    :param T: Time of option expiration
    :param r: Annualized risk-free interest rate
    Outputs call and put prices in dict format, e.g. {'call': call_price, 'put': put_price} 
    '''
    #Receive inputs: S, K, sigma, T, r
    #Compute shared intermediate values: vol_sqrt_t
    #Compute d1 and d2 -> (call _d1_d2)
    #Evaluate N(d1) and N(d2) -> (call _norm_cdf) twice
    #Assemble the call price
    #Assemble the put price
    #Return the results
    raise NotImplementedError
