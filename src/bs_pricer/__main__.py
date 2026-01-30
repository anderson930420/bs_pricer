"""
Command-Line Interface (CLI) Entry Point

Responsibility:
    - Parse user arguments using configuration defaults.
    - Invoke validated pricing logic.
    - Optionally persist a run via service + repo.
    - Format and output results to stdout/stderr.

Note:
    - Defaults are imported from config.DEFAULT_PARAMS.
    - Help messages are imported from config.UI_CONFIG.
    - Persistence is optional and routed through service + repo (no IO in core).
"""

import argparse
import sys
from pathlib import Path

from .validation import price_checked
from .config import DEFAULT_PARAMS, UI_CONFIG

from .db.repo_sqlite import SQLiteRepo
from .service.pricing_service import PricingService
from .db.models import OptionType


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Black-Scholes option pricer (validated)"
    )

    parser.add_argument(
        "--S",
        type=float,
        default=DEFAULT_PARAMS["S"],
        help=f"{UI_CONFIG['S']['help']} (Default: {DEFAULT_PARAMS['S']})",
    )
    parser.add_argument(
        "--K",
        type=float,
        default=DEFAULT_PARAMS["K"],
        help=f"{UI_CONFIG['K']['help']} (Default: {DEFAULT_PARAMS['K']})",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=DEFAULT_PARAMS["sigma"],
        help=f"{UI_CONFIG['sigma']['help']} (Default: {DEFAULT_PARAMS['sigma']})",
    )
    parser.add_argument(
        "--T",
        type=float,
        default=DEFAULT_PARAMS["T"],
        help=f"{UI_CONFIG['T']['help']} (Default: {DEFAULT_PARAMS['T']})",
    )
    parser.add_argument(
        "--r",
        type=float,
        default=DEFAULT_PARAMS["r"],
        help=f"{UI_CONFIG['r']['help']} (Default: {DEFAULT_PARAMS['r']})",
    )

    # Persistence controls
    parser.add_argument(
        "--db",
        type=str,
        default="bs_pricer.sqlite3",
        help="SQLite database path for persistence (Default: bs_pricer.sqlite3)",
    )
    parser.add_argument(
        "--persist",
        dest="persist",
        action="store_true",
        default=True,
        help="Persist the run to DB via service layer (Default: enabled)",
    )
    parser.add_argument(
        "--no-persist",
        dest="persist",
        action="store_false",
        help="Do not persist; compute only",
    )

    args = parser.parse_args()

    try:
        # Always compute (keeps CLI output identical to legacy behavior)
        result = price_checked(
            S=args.S,
            K=args.K,
            sigma=args.sigma,
            T=args.T,
            r=args.r,
        )

        # Optional persistence: store a single run (CALL) via service layer
        if args.persist:
            repo = SQLiteRepo(Path(args.db))
            svc = PricingService(repo=repo)

            svc.run_point(
                S=args.S,
                K=args.K,
                T=args.T,
                sigma=args.sigma,
                r=args.r,
                option_type=OptionType.CALL,
                tags=("cli",),
            )

    except (ValueError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Output formatted results (legacy format + persist info)
    print("-" * 30)
    print("Configuration Used:")
    print(f"  Spot Price (S):   {args.S}")
    print(f"  Strike Price (K): {args.K}")
    print(f"  Volatility (σ):   {args.sigma}")
    print(f"  Time (T):         {args.T}")
    print(f"  Risk-Free (r):    {args.r}")
    print(f"  Persist:          {args.persist}")
    if args.persist:
        print(f"  DB Path:          {args.db}")
    print("-" * 30)
    print(f"Call Price: {result['call']:.4f}")
    print(f"Put Price:  {result['put']:.4f}")
    print("-" * 30)


if __name__ == "__main__":
    main()
