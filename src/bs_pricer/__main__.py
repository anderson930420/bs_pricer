"""
Command-Line Interface (CLI) Entry Point

Responsibility:
    - Parse user arguments using configuration defaults.
    - Price options (validated) and optionally persist runs via service + repo.
    - Provide basic read-side commands for persisted runs (history/show).
    - Format and output results to stdout/stderr.

Note:
    - Defaults are imported from config.DEFAULT_PARAMS.
    - Help messages are imported from config.UI_CONFIG.
    - Persistence is optional and routed through service + repo (no IO in core).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import DEFAULT_PARAMS, UI_CONFIG
from .db.models import OptionType, RunId
from .db.repo_sqlite import SQLiteRepo
from .service.pricing_service import PricingService
from .validation import price_checked


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Black-Scholes option pricer (validated)"
    )
    sub = parser.add_subparsers(dest="cmd")

    # ---- price ----
    p_price = sub.add_parser(
        "price",
        help="Price (and optionally persist)",
        description="Compute call/put prices via validated engine. Optionally persist a run.",
    )

    p_price.add_argument(
        "--S",
        type=float,
        default=DEFAULT_PARAMS["S"],
        help=f"{UI_CONFIG['S']['help']} (Default: {DEFAULT_PARAMS['S']})",
    )
    p_price.add_argument(
        "--K",
        type=float,
        default=DEFAULT_PARAMS["K"],
        help=f"{UI_CONFIG['K']['help']} (Default: {DEFAULT_PARAMS['K']})",
    )
    p_price.add_argument(
        "--sigma",
        type=float,
        default=DEFAULT_PARAMS["sigma"],
        help=f"{UI_CONFIG['sigma']['help']} (Default: {DEFAULT_PARAMS['sigma']})",
    )
    p_price.add_argument(
        "--T",
        type=float,
        default=DEFAULT_PARAMS["T"],
        help=f"{UI_CONFIG['T']['help']} (Default: {DEFAULT_PARAMS['T']})",
    )
    p_price.add_argument(
        "--r",
        type=float,
        default=DEFAULT_PARAMS["r"],
        help=f"{UI_CONFIG['r']['help']} (Default: {DEFAULT_PARAMS['r']})",
    )

    # Persistence controls
    p_price.add_argument(
        "--db",
        type=str,
        default="bs_pricer.sqlite3",
        help="SQLite database path for persistence (Default: bs_pricer.sqlite3)",
    )
    p_price.add_argument(
        "--persist",
        dest="persist",
        action="store_true",
        default=True,
        help="Persist the run to DB via service layer (Default: enabled)",
    )
    p_price.add_argument(
        "--no-persist",
        dest="persist",
        action="store_false",
        help="Do not persist; compute only",
    )

    # Which option type to persist (pricing output on screen always shows both)
    p_price.add_argument(
        "--persist-option",
        choices=["call", "put"],
        default="call",
        help="Which option value to persist when --persist is enabled (Default: call)",
    )

    # ---- history ----
    p_hist = sub.add_parser(
        "history",
        help="List recent persisted runs",
        description="List recent persisted pricing runs.",
    )
    p_hist.add_argument(
        "--db",
        type=str,
        default="bs_pricer.sqlite3",
        help="SQLite database path (Default: bs_pricer.sqlite3)",
    )
    p_hist.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max number of runs to list (Default: 20)",
    )

    # ---- show ----
    p_show = sub.add_parser(
        "show",
        help="Show a persisted run by run_id",
        description="Display a persisted run (inputs + outputs) by run_id.",
    )
    p_show.add_argument(
        "--db",
        type=str,
        default="bs_pricer.sqlite3",
        help="SQLite database path (Default: bs_pricer.sqlite3)",
    )
    p_show.add_argument(
        "--run-id",
        required=True,
        help="Run id to load (as printed by history/price persist)",
    )

    return parser


def _print_price_output(*, S: float, K: float, sigma: float, T: float, r: float, persist: bool, db: str, result: dict) -> None:
    print("-" * 30)
    print("Configuration Used:")
    print(f"  Spot Price (S):   {S}")
    print(f"  Strike Price (K): {K}")
    print(f"  Volatility (σ):   {sigma}")
    print(f"  Time (T):         {T}")
    print(f"  Risk-Free (r):    {r}")
    print(f"  Persist:          {persist}")
    if persist:
        print(f"  DB Path:          {db}")
    print("-" * 30)
    print(f"Call Price: {result['call']:.4f}")
    print(f"Put Price:  {result['put']:.4f}")
    print("-" * 30)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # Backward-compatible default:
    # `python -m bs_pricer` behaves like `python -m bs_pricer price`
    cmd = args.cmd or "price"

    if cmd == "price":
        try:
            # Always compute (keeps CLI output stable and complete)
            result = price_checked(
                S=args.S,
                K=args.K,
                sigma=args.sigma,
                T=args.T,
                r=args.r,
            )

            # Optional persistence: store exactly one option type per run via service layer
            if args.persist:
                repo = SQLiteRepo(Path(args.db))
                svc = PricingService(repo=repo)

                opt = OptionType.CALL if args.persist_option == "call" else OptionType.PUT

                run = svc.run_point(
                    S=args.S,
                    K=args.K,
                    T=args.T,
                    sigma=args.sigma,
                    r=args.r,
                    option_type=opt,
                    tags=("cli",),
                )
                # Provide the run id for later retrieval
                print(f"run_id={run.run_id}")

        except (ValueError, TypeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)

        _print_price_output(
            S=args.S,
            K=args.K,
            sigma=args.sigma,
            T=args.T,
            r=args.r,
            persist=args.persist,
            db=args.db,
            result=result,
        )
        return

    if cmd == "history":
        repo = SQLiteRepo(Path(args.db))
        ids = list(repo.list_pricing_runs(limit=args.limit))
        if not ids:
            print("No runs found.")
            return

        print("run_id\tasof_utc\topt\tprice")
        for rid in ids:
            run = repo.get_pricing_run(rid)
            if run is None:
                continue
            print(
                f"{run.run_id}\t"
                f"{run.inputs.asof_utc.isoformat()}\t"
                f"{run.outputs.option_type.value}\t"
                f"{run.outputs.price}"
            )
        return

    if cmd == "show":
        repo = SQLiteRepo(Path(args.db))
        rid = RunId(args.run_id)

        run = repo.get_pricing_run(rid)
        if run is None:
            print("Not found.", file=sys.stderr)
            sys.exit(1)

        print("-" * 30)
        print(f"run_id:      {run.run_id}")
        print(f"asof_utc:    {run.inputs.asof_utc.isoformat()}")
        if run.inputs.instrument_id is not None:
            print(f"instrument:  {run.inputs.instrument_id}")
        if run.inputs.tags:
            print(f"tags:        {', '.join(run.inputs.tags)}")
        if run.inputs.notes:
            print(f"notes:       {run.inputs.notes}")
        print("-" * 30)
        print("Inputs:")
        print(f"  S={run.inputs.S} K={run.inputs.K} T={run.inputs.T} sigma={run.inputs.sigma} r={run.inputs.r}")
        print(f"  option_type={run.inputs.option_type.value}")
        print("-" * 30)
        print("Outputs:")
        print(f"  option_type={run.outputs.option_type.value}")
        print(f"  price={run.outputs.price}")
        if run.outputs.engine:
            print(f"  engine={run.outputs.engine}")
        if run.outputs.engine_version:
            print(f"  engine_version={run.outputs.engine_version}")
        print("-" * 30)
        return

    # Should be unreachable due to controlled subcommands, but keep a hard fail.
    print(f"Unknown command: {cmd}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
