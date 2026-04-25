# coding: utf-8
"""
Best 60m Rep Push Profile – Rep Comparison
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(layout="wide")

# =========================================================
# COLOURS
# =========================================================
REP_COLOURS = {
    "60m_1": "#2ca02c",   # green
    "60m_3": "#46A9D6",   # light blue
}

BAR_COLOURS = {
    "push_length": {
        "60m_1": "#1f8f3a",
        "60m_3": "#1f6fae",
    },
    "rolling_length": {
        "60m_1": "#8fd19e",
        "60m_3": "#9ccfe8",
    },
}

REP_LABELS = {
    "60m_1": "Best Rep",
    "60m_3": "60m_3",
}

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(show_spinner=False)
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    df = pd.read_excel(data_path)

    df["trial_id"] = df["trial_id"].astype(str).str.strip()
    df["metric_key"] = df["metric_key"].astype(str).str.strip()
    df["distance_band"] = (
        df["distance_band"]
        .astype(str)
        .str.replace("–", "-", regex=False)
        .str.replace("−", "-", regex=False)
        .str.strip()
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df

df = load_data()

# =========================================================
# TITLE
# =========================================================
st.title("Best 60m Push Profile – Rep Comparison")
st.write(
    "Cycle length composition showing stacked push and rolling distances "
    "with total cycle length overlaid."
)

# =========================================================
# SHARED SETTINGS
# =========================================================
DISTANCE_BANDS = ["0-10", "35-45"]
REPS = ["60m_1", "60m_3"]

REP_OFFSET = {"60m_1": -0.18, "60m_3": 0.18}
TEXT_OFFSET = {
    "0-10": {
        "60m_1": 0.28,
        "60m_3": 0.38,
    },
    "35-45": {
        "60m_1": 0.4,
        "60m_3": 0.45,
    },
}

Y_MAX = 3.5          # ✅ fixed y axis
TEXT_SIZE = 14       # ✅ larger annotation text

#

# =========================================================
# VIEW B — SIDE‑BY‑SIDE COMPARISON (ONE ROW)
# =========================================================
st.subheader("Cycle Length Breakdown – Side‑by‑Side View")

col_left, col_right = st.columns(2)

for col, band in zip([col_left, col_right], DISTANCE_BANDS):
    with col:

        df_len = df[
            (df["metric_key"].isin(["push_length", "rolling_length"])) &
            (df["distance_band"] == band) &
            (df["trial_id"].isin(REPS))
        ]

        fig = go.Figure()
        cycles = sorted(df_len["cycle_no"].unique())

        for rep in REPS:
            r = df_len[df_len["trial_id"] == rep].sort_values("cycle_no")
            push = r[r["metric_key"] == "push_length"]
            roll = r[r["metric_key"] == "rolling_length"]

            x = push["cycle_no"].values + REP_OFFSET[rep]
            total = push["value"].values + roll["value"].values

            fig.add_bar(
                x=x,
                y=push["value"],
                width=0.32,
                marker_color=BAR_COLOURS["push_length"][rep],
                showlegend=False,
            )

            fig.add_bar(
                x=x,
                y=roll["value"],
                width=0.32,
                base=push["value"],
                marker_color=BAR_COLOURS["rolling_length"][rep],
                showlegend=False,
            )

            fig.add_scatter(
                x=x,
                y=total + TEXT_OFFSET[band][rep],
                mode="lines+markers+text",
                marker=dict(size=7, color=REP_COLOURS[rep]),
                line=dict(
                    color=REP_COLOURS[rep],
                    width=2,
                    dash="solid" if rep == "60m_1" else "dash",
                ),
                text=[f"{v:.2f}" for v in total],
                textfont=dict(size=TEXT_SIZE, color=REP_COLOURS[rep]),
                textposition="top center",
                showlegend=False,
            )

        fig.update_layout(
            title=f"Cycle Length ({band} m)",
            barmode="stack",
            template="simple_white",
            height=420,
            yaxis=dict(range=[0, Y_MAX]),
            xaxis=dict(tickmode="array", tickvals=cycles),
        )

        st.plotly_chart(fig, use_container_width=True)