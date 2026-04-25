"""Repo-root import shim for the src-layout package.

This keeps `python -m bs_pricer` working from a fresh checkout when the package
has not been installed into the active environment.
"""

from __future__ import annotations

from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "bs_pricer"
if _SRC_PACKAGE.is_dir():
    __path__.append(str(_SRC_PACKAGE))
