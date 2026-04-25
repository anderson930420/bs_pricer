from __future__ import annotations

import ast
from pathlib import Path

import numpy as np

from bs_pricer.config import GRID_CONFIG
from bs_pricer.surface_grid import surface_axes, surface_grid_config


def test_surface_grid_config_uses_canonical_keys() -> None:
    cfg = {
        "SPOT_MIN_PCT": 0.8,
        "SPOT_MAX_PCT": 1.2,
        "SPOT_STEPS": 12,
        "VOL_MIN": 0.1,
        "VOL_MAX": 0.4,
        "VOL_STEPS": 7,
    }

    grid = surface_grid_config(spot_price=125.0, grid_config=cfg)

    assert grid.spot_min == 100.0
    assert grid.spot_max == 150.0
    assert grid.vol_min == 0.1
    assert grid.vol_max == 0.4
    assert grid.spot_steps == 12
    assert grid.vol_steps == 7


def test_default_surface_grid_is_10_by_10() -> None:
    grid = surface_grid_config(spot_price=100.0)
    spot_axis, sigma_axis = surface_axes(spot_price=100.0)

    assert GRID_CONFIG["SPOT_STEPS"] == 10
    assert GRID_CONFIG["VOL_STEPS"] == 10
    assert grid.spot_steps == 10
    assert grid.vol_steps == 10
    assert len(spot_axis) == 10
    assert len(sigma_axis) == 10


def test_surface_grid_config_does_not_require_stale_keys() -> None:
    cfg = {
        "SPOT_MIN_PCT": 0.9,
        "SPOT_MAX_PCT": 1.1,
        "SPOT_STEPS": 5,
        "VOL_MIN": 0.05,
        "VOL_MAX": 0.25,
        "VOL_STEPS": 4,
    }

    grid = surface_grid_config(spot_price=200.0, grid_config=cfg)
    spot_axis, sigma_axis = surface_axes(spot_price=200.0, grid_config=cfg)

    assert np.isclose(grid.spot_min, 180.0)
    assert np.isclose(grid.spot_max, 220.0)
    assert len(spot_axis) == 5
    assert len(sigma_axis) == 4
    assert np.allclose(spot_axis, np.linspace(180.0, 220.0, 5))
    assert np.allclose(sigma_axis, np.linspace(0.05, 0.25, 4))


def test_surface_grid_changes_when_canonical_config_changes() -> None:
    base_cfg = {
        "SPOT_MIN_PCT": 0.5,
        "SPOT_MAX_PCT": 1.5,
        "SPOT_STEPS": 3,
        "VOL_MIN": 0.1,
        "VOL_MAX": 0.3,
        "VOL_STEPS": 3,
    }
    updated_cfg = {
        "SPOT_MIN_PCT": 0.6,
        "SPOT_MAX_PCT": 1.4,
        "SPOT_STEPS": 4,
        "VOL_MIN": 0.2,
        "VOL_MAX": 0.5,
        "VOL_STEPS": 6,
    }

    base_axes = surface_axes(spot_price=100.0, grid_config=base_cfg)
    updated_axes = surface_axes(spot_price=100.0, grid_config=updated_cfg)

    assert base_axes != updated_axes
    assert len(base_axes[0]) == 3
    assert len(updated_axes[0]) == 4
    assert base_axes[0][0] == 50.0
    assert updated_axes[0][0] == 60.0


def test_surface_module_does_not_import_config() -> None:
    import bs_pricer.surface as surface_module

    source = Path(surface_module.__file__).read_text()
    tree = ast.parse(source)

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert "bs_pricer.config" not in imported_modules
    assert "config" not in imported_modules
