from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np

from .config import GRID_CONFIG


@dataclass(frozen=True, slots=True)
class SurfaceGridConfig:
    spot_min: float
    spot_max: float
    vol_min: float
    vol_max: float
    spot_steps: int
    vol_steps: int


def surface_grid_config(
    spot_price: float,
    grid_config: Mapping[str, Any] | None = None,
) -> SurfaceGridConfig:
    cfg = GRID_CONFIG if grid_config is None else grid_config
    return SurfaceGridConfig(
        spot_min=float(spot_price) * float(cfg["SPOT_MIN_PCT"]),
        spot_max=float(spot_price) * float(cfg["SPOT_MAX_PCT"]),
        vol_min=float(cfg["VOL_MIN"]),
        vol_max=float(cfg["VOL_MAX"]),
        spot_steps=int(cfg["SPOT_STEPS"]),
        vol_steps=int(cfg["VOL_STEPS"]),
    )


def surface_axes(
    spot_price: float,
    grid_config: Mapping[str, Any] | None = None,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    grid = surface_grid_config(spot_price, grid_config=grid_config)
    spot_axis = tuple(np.linspace(grid.spot_min, grid.spot_max, grid.spot_steps, dtype=float).tolist())
    sigma_axis = tuple(np.linspace(grid.vol_min, grid.vol_max, grid.vol_steps, dtype=float).tolist())
    return spot_axis, sigma_axis
