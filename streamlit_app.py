"""
Streamlit Cloud entrypoint.

This thin wrapper exists so the deployed app can be launched from the
repository root while the actual application logic lives inside the
`src/bs_pricer` package.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from bs_pricer.app_streamlit import main  # noqa: E402

if __name__ == "__main__":
    main()