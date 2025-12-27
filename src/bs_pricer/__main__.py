# __main__.py
import argparse
import sys
from .validation import price_checked

def main():
    parser = argparse.ArgumentParser(
        description="Black-Scholes option pricer (validated)"
    )

    parser.add_argument("--S", type=float, required=True, help="Spot price")
    parser.add_argument("--K", type=float, required=True, help="Strike price")
    parser.add_argument("--sigma", type=float, required=True, help="Volatility")
    parser.add_argument("--T", type=float, required=True, help="Time to maturity")
    parser.add_argument("--r", type=float, required=True, help="Risk-free rate")

    args = parser.parse_args()

    try:
        result = price_checked(
            args.S,
            args.K,
            args.sigma,
            args.T,
            args.r
        )
    except (ValueError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"call price={result['call']}")
    print(f"put price={result['put']}")

if __name__ == "__main__":
    main()

