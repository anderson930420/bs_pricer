from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st

from bs_pricer.config import DEFAULT_PARAMS, UI_CONFIG
from bs_pricer.scenario import SCENARIO_PRESETS, analyze_scenario
from bs_pricer.surface import value_surface
from bs_pricer.surface_grid import surface_grid_config
from bs_pricer.validation import greeks_checked, price_checked

from bs_pricer.portfolio.models import InstrumentId, Side, Trade
from bs_pricer.portfolio.pnl import InventoryError, apply_trades_fifo, unrealized_pnl_from_lots


def _slider_float(key: str) -> float:
    """
    Read slider spec from UI_CONFIG and return a float.
    Expects UI_CONFIG[key] to provide min/max/step/help/label-ish fields.
    Falls back gracefully if some fields don't exist.
    """
    cfg = UI_CONFIG[key]
    label = cfg.get("label", key)
    help_ = cfg.get("help", None)
    vmin = float(cfg.get("min", 0.0))
    vmax = float(cfg.get("max", 1.0))
    step = float(cfg.get("step", (vmax - vmin) / 100.0)) if cfg.get("step") is not None else None
    default = float(DEFAULT_PARAMS[key])

    return float(
        st.sidebar.slider(
            label,
            min_value=vmin,
            max_value=vmax,
            value=default,
            step=step,
            help=help_,
        )
    )


def _axis_from_range(*, lo: float, hi: float, n: int) -> tuple[float, ...]:
    if n < 2:
        raise ValueError("n must be >= 2")
    if hi <= lo:
        raise ValueError("hi must be > lo")
    return tuple(np.linspace(lo, hi, n, dtype=float).tolist())


def _heatmap_dataframe(matrix: list[list[float]], sigma_axis: tuple[float, ...], S_axis: tuple[float, ...]) -> pd.DataFrame:
    # matrix shape in your surface layer is (len(sigma_axis), len(S_axis))
    df = pd.DataFrame(matrix, index=list(sigma_axis), columns=list(S_axis))
    df.index.name = "Volatility"
    df.columns.name = "Spot Price"
    return df


def _parse_ts_utc(s: str) -> datetime:
    # Expect ISO8601; accept trailing "Z"
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        raise ValueError("ts_utc must be timezone-aware (include 'Z' or offset)")
    return dt.astimezone(timezone.utc)


def _parse_trade(obj: dict) -> Trade:
    inst = InstrumentId(str(obj["instrument_id"]))
    ts = _parse_ts_utc(str(obj["ts_utc"]))
    side = Side(str(obj["side"]))
    qty = float(obj["qty"])
    price = float(obj["price"])
    fees = float(obj.get("fees", 0.0))
    return Trade(
        instrument_id=inst,
        ts_utc=ts,
        side=side,
        qty=qty,
        price=price,
        fees=fees,
        venue=obj.get("venue"),
        trade_id=obj.get("trade_id"),
    )


def main() -> None:
    st.set_page_config(page_title="Black–Scholes Pricing Model", layout="wide")

    st.title("Black–Scholes Pricing Model")

    # ---- Sidebar: Base Inputs ----
    st.sidebar.header("Parameters")

    S = _slider_float("S")
    K = _slider_float("K")
    T = _slider_float("T")
    sigma = _slider_float("sigma")
    r = _slider_float("r")

    selected_option = st.sidebar.radio(
        "Selected option",
        options=("call", "put"),
        format_func=lambda x: "Long Call" if x == "call" else "Long Put",
        horizontal=True,
    )

    # ---- Sidebar: Heatmap Params ----
    st.sidebar.divider()
    st.sidebar.subheader("Heatmap Parameters")

    grid_defaults = surface_grid_config(S)
    spot_min_default = grid_defaults.spot_min
    spot_max_default = grid_defaults.spot_max
    vol_min_default = grid_defaults.vol_min
    vol_max_default = grid_defaults.vol_max
    n_spot_default = grid_defaults.spot_steps
    n_vol_default = grid_defaults.vol_steps

    spot_min = float(st.sidebar.number_input("Min Spot Price", value=spot_min_default, step=1.0))
    spot_max = float(st.sidebar.number_input("Max Spot Price", value=spot_max_default, step=1.0))
    vol_min = float(st.sidebar.number_input("Min Volatility for Heatmap", value=vol_min_default, step=0.01, format="%.2f"))
    vol_max = float(st.sidebar.number_input("Max Volatility for Heatmap", value=vol_max_default, step=0.01, format="%.2f"))

    n_spot = int(st.sidebar.slider("Spot grid points", min_value=5, max_value=60, value=n_spot_default, step=1))
    n_vol = int(st.sidebar.slider("Vol grid points", min_value=5, max_value=60, value=n_vol_default, step=1))

    heatmap_mode = st.sidebar.radio(
        "Heatmap Mode",
        options=("Price", "PnL"),
        horizontal=True,
    )

    entry_price = None
    quantity = None
    position_direction = None
    if heatmap_mode == "PnL":
        entry_price = float(
            st.sidebar.number_input(
                "Entry Price",
                min_value=0.0,
                value=10.0,
                step=0.01,
                format="%.4f",
            )
        )
        quantity = float(
            st.sidebar.number_input(
                "Quantity",
                min_value=0.0,
                value=1.0,
                step=1.0,
                format="%.4f",
            )
        )
        position_direction = st.sidebar.radio(
            "Position Direction",
            options=("Long", "Short"),
            horizontal=True,
        )

    show_cell_values = st.sidebar.toggle("Annotate heatmap values", value=True)
    decimals = int(st.sidebar.slider("Annotation decimals", min_value=0, max_value=4, value=2, step=1))

    # ---- Point price and shared validated base result ----
    try:
        res = price_checked(S=S, K=K, sigma=sigma, T=T, r=r)
        call_px = float(res["call"])
        put_px = float(res["put"])
        err_msg = None
    except Exception as e:
        call_px, put_px = float("nan"), float("nan")
        err_msg = str(e)

    if err_msg:
        st.error(f"Input error: {err_msg}")
        st.stop()

    price_tab, scenario_tab, surfaces_tab = st.tabs(["Price & Greeks", "Scenario Analysis", "Surfaces"])

    with price_tab:
        price_cols = st.columns(2, gap="large")
        with price_cols[0]:
            st.metric(label="CALL Value", value=f"${call_px:,.4f}")
        with price_cols[1]:
            st.metric(label="PUT Value", value=f"${put_px:,.4f}")

        try:
            greek_values = greeks_checked(S=S, K=K, sigma=sigma, T=T, r=r)
        except ValueError as e:
            st.info(f"Analytic Greeks unavailable: {e}")
        else:
            rows = []
            for label, values in (("Call", greek_values.call), ("Put", greek_values.put)):
                rows.append(
                    {
                        "Option": label,
                        "Delta": values.delta,
                        "Gamma": values.gamma,
                        "Vega": values.vega,
                        "Vega / vol point": values.vega * 0.01,
                        "Theta": values.theta,
                        "Daily theta": values.theta / 365.0,
                        "Rho": values.rho,
                        "Rho / rate point": values.rho * 0.01,
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with scenario_tab:
        base_price = call_px if selected_option == "call" else put_px
        st.subheader(f"Analyzing: {'Long Call' if selected_option == 'call' else 'Long Put'}")
        st.metric("Base price", f"${base_price:,.4f}")

        preset = st.selectbox(
            "Preset scenario",
            options=SCENARIO_PRESETS,
            format_func=lambda shift: shift.name,
        )
        st.caption(preset.description)

        try:
            scenario_result = analyze_scenario(
                S=S,
                K=K,
                sigma=sigma,
                T=T,
                r=r,
                option_type=selected_option,
                shift=preset,
            )
        except Exception as e:
            st.error(f"Scenario error: {e}")
        else:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Input": item.name,
                            "Before": item.display_before,
                            "After": item.display_after,
                        }
                        for item in scenario_result.changed_inputs
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )
            if scenario_result.reached_expiry:
                st.info("This scenario reaches expiry; scenario price uses expiration payoff.")

            result_cols = st.columns(3, gap="large")
            with result_cols[0]:
                st.metric("Scenario price", f"${scenario_result.scenario_price:,.4f}")
            with result_cols[1]:
                st.metric("Actual repricing change", f"{scenario_result.actual_change:,.4f}")
            with result_cols[2]:
                st.metric("First-order approximate change", f"{scenario_result.bridge.first_order_approx_change:,.4f}")

            st.subheader("Price Bridge")
            st.dataframe(
                pd.DataFrame(
                    [
                        {"Component": "Delta", "Effect": scenario_result.bridge.delta_effect},
                        {"Component": "Vega", "Effect": scenario_result.bridge.vega_effect},
                        {"Component": "Theta", "Effect": scenario_result.bridge.theta_effect},
                        {"Component": "Rho", "Effect": scenario_result.bridge.rho_effect},
                        {"Component": "First-order approximation", "Effect": scenario_result.bridge.first_order_approx_change},
                        {"Component": "Actual repricing change", "Effect": scenario_result.actual_change},
                        {"Component": "Residual", "Effect": scenario_result.bridge.residual_change},
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(scenario_result.rho_caveat)
            st.caption(scenario_result.residual_caveat)

    with surfaces_tab:
        st.header("Options Heatmap")
        if heatmap_mode == "Price":
            st.caption("Explore how option prices fluctuate with varying Spot Prices and Volatility, while holding Strike constant.")
        else:
            st.caption("Explore option PnL across the same Spot Price and Volatility grid using the current surface, entry price, quantity, and position direction.")

        try:
            S_axis = _axis_from_range(lo=spot_min, hi=spot_max, n=n_spot)
            sigma_axis = _axis_from_range(lo=vol_min, hi=vol_max, n=n_vol)
        except Exception as e:
            st.error(f"Heatmap range error: {e}")
            st.stop()

        vs = value_surface(
            S_axis=S_axis,
            sigma_axis=sigma_axis,
            K=K,
            T=T,
            r=r,
            engine=price_checked,
        )

        if heatmap_mode == "Price":
            call_matrix = vs.call
            put_matrix = vs.put
            colorbar_title = "Option Value"
            call_heatmap_kwargs: dict[str, object] = {"colorscale": "Blues"}
            put_heatmap_kwargs: dict[str, object] = {"colorscale": "Oranges"}
            left_chart_label = "Call Price Heatmap"
            right_chart_label = "Put Price Heatmap"
            debug_call_label = "Call price matrix"
            debug_put_label = "Put price matrix"
        else:
            assert entry_price is not None
            assert quantity is not None
            assert position_direction is not None
            direction_sign = 1.0 if position_direction == "Long" else -1.0
            pnl_scale = direction_sign * quantity
            call_matrix = (vs.call - entry_price) * pnl_scale
            put_matrix = (vs.put - entry_price) * pnl_scale
            colorbar_title = "PnL"
            pnl_bound = float(max(np.abs(call_matrix).max(), np.abs(put_matrix).max(), 0.0))
            if pnl_bound == 0.0:
                pnl_bound = 1.0
            pnl_heatmap_kwargs = {
                "colorscale": [
                    (0.0, "#7f0000"),
                    (0.2, "#d7301f"),
                    (0.5, "#f7f7f7"),
                    (0.8, "#1a9850"),
                    (1.0, "#00441b"),
                ],
                "zmin": -pnl_bound,
                "zmax": pnl_bound,
            }
            left_chart_label = "Call PnL Heatmap"
            right_chart_label = "Put PnL Heatmap"
            debug_call_label = "Call PnL matrix"
            debug_put_label = "Put PnL matrix"
            call_heatmap_kwargs = pnl_heatmap_kwargs
            put_heatmap_kwargs = pnl_heatmap_kwargs

        call_df = _heatmap_dataframe(call_matrix.tolist(), sigma_axis=sigma_axis, S_axis=S_axis)
        put_df = _heatmap_dataframe(put_matrix.tolist(), sigma_axis=sigma_axis, S_axis=S_axis)

        import plotly.figure_factory as ff  # local import to keep import-time light
        import plotly.graph_objects as go

        def make_heatmap(df: pd.DataFrame, title: str, heatmap_kwargs: dict[str, object]) -> go.Figure:
            z = df.values
            x = df.columns.astype(float).tolist()
            y = df.index.astype(float).tolist()
            x_labels = [f"{c:.2f}" for c in x]
            y_labels = [f"{i:.2f}" for i in y]

            z_list = z.tolist()
            annotation_text = None
            if show_cell_values:
                annotation_text = [[f"{v:.{decimals}f}" for v in row] for row in z_list]

            fig = ff.create_annotated_heatmap(
                z=z_list,
                x=x,
                y=y,
                annotation_text=annotation_text,
                showscale=True,
                hoverinfo="z",
                colorbar=dict(title=colorbar_title),
                **heatmap_kwargs,
            )
            fig.update_layout(
                title=title,
                xaxis_title="Spot Price",
                yaxis_title="Volatility",
                margin=dict(l=40, r=20, t=60, b=40),
            )
            if heatmap_mode == "PnL" and show_cell_values:
                neutral_threshold = 0.15 * float(heatmap_kwargs["zmax"])
                for annotation, value in zip(fig.layout.annotations, z.flatten(), strict=False):
                    annotation.font.color = "#111111" if abs(float(value)) <= neutral_threshold else "#FFFFFF"
            fig.update_xaxes(
                tickmode="array",
                tickvals=x,
                ticktext=x_labels,
            )
            fig.update_yaxes(
                tickmode="array",
                tickvals=y,
                ticktext=y_labels,
            )
            return fig

        hm_cols = st.columns(2, gap="large")

        with hm_cols[0]:
            st.subheader(left_chart_label)
            st.plotly_chart(make_heatmap(call_df, "CALL", call_heatmap_kwargs), use_container_width=True)

        with hm_cols[1]:
            st.subheader(right_chart_label)
            st.plotly_chart(make_heatmap(put_df, "PUT", put_heatmap_kwargs), use_container_width=True)

        with st.expander("Show raw matrices (debug)"):
            st.write(debug_call_label)
            st.dataframe(call_df)
            st.write(debug_put_label)
            st.dataframe(put_df)

        st.divider()
        st.subheader("PnL (FIFO)")
        st.caption(
            "Compute FIFO PnL from trades using a selected mark price. "
            "Trades are not persisted in this version."
        )

        mark_choice = st.radio(
            "Mark price source",
            options=("Use CALL price", "Use PUT price", "Custom mark"),
            horizontal=True,
        )

        if mark_choice == "Use CALL price":
            mark_price = call_px
        elif mark_choice == "Use PUT price":
            mark_price = put_px
        else:
            mark_price = float(
                st.number_input(
                    "Custom mark price",
                    value=12.3456,
                    step=0.0001,
                    format="%.6f",
                    help="Manual mark for sanity-checking FIFO PnL (no unit enforcement in this UI layer).",
                )
            )

        default_trades_json = [
            {
                "instrument_id": "AAPL",
                "ts_utc": "2026-01-01T00:00:00Z",
                "side": "BUY",
                "qty": 1.0,
                "price": 90.0,
                "fees": 0.0,
            },
            {
                "instrument_id": "AAPL",
                "ts_utc": "2026-01-02T00:00:00Z",
                "side": "SELL",
                "qty": 0.5,
                "price": 95.0,
                "fees": 0.0,
            },
        ]

        trades_text = st.text_area(
            "Trades (JSON list)",
            value=json.dumps(default_trades_json, indent=2),
            height=220,
        )

        pnl_cols = st.columns(3, gap="large")

        try:
            raw = json.loads(trades_text)
            if not isinstance(raw, list) or len(raw) == 0:
                raise ValueError("Trades JSON must be a non-empty list")

            trades = [_parse_trade(x) for x in raw]
            lots, realized = apply_trades_fifo(trades)
            unreal = 0.0
            if lots:
                unrealized = unrealized_pnl_from_lots(lots, mark_price=mark_price)
                unreal = float(unrealized.unrealized)

            net = float(realized.realized) + unreal

            with pnl_cols[0]:
                st.metric("Realized PnL", f"{realized.realized:,.4f}")
                st.caption(f"Fees total: {realized.fees:,.4f}")

            with pnl_cols[1]:
                st.metric("Unrealized PnL", f"{unreal:,.4f}")
                st.caption(f"Mark price: {mark_price:,.6f}")

            with pnl_cols[2]:
                st.metric("Net PnL", f"{net:,.4f}")

            with st.expander("Open lots (FIFO inventory)"):
                if not lots:
                    st.write("No open lots.")
                else:
                    st.dataframe(
                        [
                            {
                                "ts_utc": lot.ts_utc.isoformat(),
                                "qty": lot.qty,
                                "cost_per_unit": lot.cost_per_unit,
                                "source_trade_id": lot.source_trade_id,
                            }
                            for lot in lots
                        ],
                        use_container_width=True,
                    )

        except InventoryError as e:
            st.error(f"Inventory error (FIFO): {e}")
        except Exception as e:
            st.error(f"PnL input error: {e}")


if __name__ == "__main__":
    main()
