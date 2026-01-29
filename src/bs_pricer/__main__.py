"""
Command-Line Interface (CLI) Entry Point

Responsibility:
    - Parse user arguments using configuration defaults.
    - Invoke the validation and pricing logic.
    - Format and output results to stdout/stderr.

Note:
    - Defaults are imported from config.DEFAULT_PARAMS.
    - Help messages are imported from config.UI_CONFIG.
    - No database logic is included in this version.
"""

import argparse
import sys
from .validation import price_checked
from .config import DEFAULT_PARAMS, UI_CONFIG

def main():
    parser = argparse.ArgumentParser(
        description="Black-Scholes option pricer (validated)"
    )

    # Define arguments dynamically using the centralized config
    # This ensures consistency between CLI and other interfaces (like Streamlit)
    
    parser.add_argument(
        "--S", 
        type=float, 
        default=DEFAULT_PARAMS["S"], 
        help=f"{UI_CONFIG['S']['help']} (Default: {DEFAULT_PARAMS['S']})"
    )
    parser.add_argument(
        "--K", 
        type=float, 
        default=DEFAULT_PARAMS["K"], 
        help=f"{UI_CONFIG['K']['help']} (Default: {DEFAULT_PARAMS['K']})"
    )
    parser.add_argument(
        "--sigma", 
        type=float, 
        default=DEFAULT_PARAMS["sigma"], 
        help=f"{UI_CONFIG['sigma']['help']} (Default: {DEFAULT_PARAMS['sigma']})"
    )
    parser.add_argument(
        "--T", 
        type=float, 
        default=DEFAULT_PARAMS["T"], 
        help=f"{UI_CONFIG['T']['help']} (Default: {DEFAULT_PARAMS['T']})"
    )
    parser.add_argument(
        "--r", 
        type=float, 
        default=DEFAULT_PARAMS["r"], 
        help=f"{UI_CONFIG['r']['help']} (Default: {DEFAULT_PARAMS['r']})"
    )

    args = parser.parse_args()

    try:
        # Pass parsed arguments to the validated pricing engine
        result = price_checked(
            S=args.S,
            K=args.K,
            sigma=args.sigma,
            T=args.T,
            r=args.r
        )
    except (ValueError, TypeError) as e:
        # Output errors to stderr so they don't mix with valid output
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Output formatted results
    print("-" * 30)
    print(f"Configuration Used:")
    print(f"  Spot Price (S):   {args.S}")
    print(f"  Strike Price (K): {args.K}")
    print(f"  Volatility (σ):   {args.sigma}")
    print(f"  Time (T):         {args.T}")
    print(f"  Risk-Free (r):    {args.r}")
    print("-" * 30)
    print(f"Call Price: {result['call']:.4f}")
    print(f"Put Price:  {result['put']:.4f}")
    print("-" * 30)

if __name__ == "__main__":
    main()