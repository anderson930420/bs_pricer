from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from bs_pricer.config import DEFAULT_PARAMS, UI_CONFIG, GRID_CONFIG
from bs_pricer.validation import price_checked
from bs_pricer.surface import value_surface


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

    # ---- Sidebar: Heatmap Params ----
    st.sidebar.divider()
    st.sidebar.subheader("Heatmap Parameters")

    # Use GRID_CONFIG as the single source of truth for resolution/default ranges
    spot_min_default = float(GRID_CONFIG.get("S_min", 80.0))
    spot_max_default = float(GRID_CONFIG.get("S_max", 120.0))
    vol_min_default = float(GRID_CONFIG.get("sigma_min", 0.10))
    vol_max_default = float(GRID_CONFIG.get("sigma_max", 0.30))
    n_spot_default = int(GRID_CONFIG.get("S_n", 10))
    n_vol_default = int(GRID_CONFIG.get("sigma_n", 10))

    spot_min = float(st.sidebar.number_input("Min Spot Price", value=spot_min_default, step=1.0))
    spot_max = float(st.sidebar.number_input("Max Spot Price", value=spot_max_default, step=1.0))
    vol_min = float(st.sidebar.number_input("Min Volatility for Heatmap", value=vol_min_default, step=0.01, format="%.2f"))
    vol_max = float(st.sidebar.number_input("Max Volatility for Heatmap", value=vol_max_default, step=0.01, format="%.2f"))

    n_spot = int(st.sidebar.slider("Spot grid points", min_value=5, max_value=60, value=n_spot_default, step=1))
    n_vol = int(st.sidebar.slider("Vol grid points", min_value=5, max_value=60, value=n_vol_default, step=1))

    show_cell_values = st.sidebar.toggle("Annotate heatmap values", value=True)
    decimals = int(st.sidebar.slider("Annotation decimals", min_value=0, max_value=4, value=2, step=1))

    # ---- Top: Point Price (Call/Put) ----
    try:
        res = price_checked(S=S, K=K, sigma=sigma, T=T, r=r)
        call_px = float(res["call"])
        put_px = float(res["put"])
        err_msg = None
    except Exception as e:
        call_px, put_px = float("nan"), float("nan")
        err_msg = str(e)

    top_cols = st.columns(2, gap="large")
    with top_cols[0]:
        st.metric(label="CALL Value", value=f"${call_px:,.4f}" if np.isfinite(call_px) else "—")
    with top_cols[1]:
        st.metric(label="PUT Value", value=f"${put_px:,.4f}" if np.isfinite(put_px) else "—")

    if err_msg:
        st.error(f"Input error: {err_msg}")
        st.stop()

    # ---- Surface / Heatmaps ----
    st.header("Options Price - Interactive Heatmap")
    st.caption("Explore how option prices fluctuate with varying Spot Prices and Volatility, while holding Strike constant.")

    # Build axes
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
        # engine default is price_checked (in your surface module), keep it explicit for clarity:
        engine=price_checked,
    )

    call_df = _heatmap_dataframe(vs.call.tolist(), sigma_axis=sigma_axis, S_axis=S_axis)
    put_df = _heatmap_dataframe(vs.put.tolist(), sigma_axis=sigma_axis, S_axis=S_axis)

    # Use plotly for annotated heatmap; Streamlit renders nicely.
    import plotly.figure_factory as ff  # local import to keep import-time light
    import plotly.graph_objects as go

    def make_heatmap(df: pd.DataFrame, title: str) -> go.Figure:
        z = df.values
        x = [f"{c:.2f}" for c in df.columns.astype(float)]
        y = [f"{i:.2f}" for i in df.index.astype(float)]

        # plotly FF annotated heatmap wants Python lists
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
        )
        fig.update_layout(
            title=title,
            xaxis_title="Spot Price",
            yaxis_title="Volatility",
            margin=dict(l=40, r=20, t=60, b=40),
        )
        return fig

    hm_cols = st.columns(2, gap="large")

    with hm_cols[0]:
        st.subheader("Call Price Heatmap")
        st.plotly_chart(make_heatmap(call_df, "CALL"), use_container_width=True)

    with hm_cols[1]:
        st.subheader("Put Price Heatmap")
        st.plotly_chart(make_heatmap(put_df, "PUT"), use_container_width=True)

    # Optional: show the underlying tables (debug / transparency)
    with st.expander("Show raw matrices (debug)"):
        st.write("Call matrix")
        st.dataframe(call_df)
        st.write("Put matrix")
        st.dataframe(put_df)


if __name__ == "__main__":
    main()
