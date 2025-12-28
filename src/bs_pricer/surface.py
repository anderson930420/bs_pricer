import numpy as np
from .validation import price_checked   # 或之後改成 engine injection
from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class ValueSurface:
    S_axis: np.ndarray        # (nS,)
    sigma_axis: np.ndarray    # (nV,)
    call: np.ndarray          # (nV, nS)
    put: np.ndarray           # (nV, nS)
    K: float
    T: float
    r: float

    def __post_init__(self):
        if self.S_axis.shape != (self.call.shape[1],):
            raise ValueError(f"S_axis shape mismatch: {self.S_axis.shape} != ({self.call.shape[1]},)")
        if self.sigma_axis.shape != (self.call.shape[0],):
            raise ValueError(f"sigma_axis shape mismatch: {self.sigma_axis.shape} != ({self.call.shape[0]},)")
        if self.call.shape != (len(self.sigma_axis), len(self.S_axis)):
            raise ValueError(f"call shape mismatch: {self.call.shape} != ({len(self.sigma_axis)}, {len(self.S_axis)})")
        if self.put.shape != self.call.shape:
            raise ValueError(f"put shape mismatch: {self.put.shape} != {self.call.shape}")

def value_surface(
    *,
    S_axis,
    sigma_axis,
    K: float,
    T: float,
    r: float,
    engine=price_checked):
    """ Compute call/put value surface on (sigma, S) grid.
        Contract:
        - Output matrices shape: (len(sigma_axis), len(S_axis))
        - engine: Callable[[float,float,float,float,float], Mapping[str,float]]
        - engine must accept (S, K, sigma, T, r) and return {"call": ..., "put": ...}
        - only enforce strictly increasing when len(sigma_axis),len(S_axis) > 1
        - call[i, j] corresponds to sigma_axis[i], S_axis[j]
        - domain/policy (e.g., S>0, sigma>=0, T=0, sigma=0) is enforced by engine 
        - this function enforces axis shape/ordering only."""
    
    S = np.asarray(S_axis, dtype=float)
    V = np.asarray(sigma_axis, dtype=float)

    if S.ndim != 1: 
        raise ValueError("S_axis must be 1D")
    if V.ndim != 1: 
        raise ValueError("sigma_axis must be 1D")
    
    if len(S) == 0:
        raise ValueError("S_axis must be non-empty")
    if len(V) == 0:
        raise ValueError("sigma_axis must be non-empty")

    if not np.isfinite(S).all(): 
        raise ValueError("S_axis must be finite")
    if not np.isfinite(V).all(): 
        raise ValueError("sigma_axis must be finite")

    if len(S) > 1 and not np.all(np.diff(S) > 0):
        raise ValueError("S_axis must be strictly increasing")
    if len(V) > 1 and not np.all(np.diff(V) > 0):
        raise ValueError("sigma_axis must be strictly increasing")

    nS = len(S)
    nV = len(V)

    call = np.empty((nV, nS), dtype=float)
    put  = np.empty((nV, nS), dtype=float)

    for i in range(nV):
        sigma = V[i]
        for j in range(nS):
            S_ = S[j]
            res = engine(S_, K, sigma, T, r)
            call[i, j] = res["call"]
            put[i, j]  = res["put"]
    return ValueSurface(S_axis=S, sigma_axis=V, call=call, put=put, K=K, T=T, r=r)
