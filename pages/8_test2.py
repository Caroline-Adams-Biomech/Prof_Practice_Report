# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 19:33:29 2026

@author: Caroline Adams
"""

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
    "This section presents cycle length composition using stacked push and rolling "
    "distances, with total cycle length overlaid for each rep."
)

# =========================================================
# CYCLE LENGTH — SINGLE PLOT, BOTH REPS
# =========================================================
st.subheader("Cycle Length Breakdown")

DISTANCE_BANDS = ["0-10", "35-45"]
REPS = ["60m_1", "60m_3"]

# Horizontal offsets (side-by-side bars)
REP_OFFSET = {
    "60m_1": -0.18,
    "60m_3":  0.18,
}

# Vertical offsets for text labels (avoid overlap)
TEXT_OFFSET = {
    "60m_1": 0.06,
    "60m_3": 0.14,
}

for band in DISTANCE_BANDS:

    st.markdown(f"**Cycle Length ({band} m)**")

    df_len = df[
        (df["metric_key"].isin(["push_length", "rolling_length"])) &
        (df["distance_band"] == band) &
        (df["trial_id"].isin(REPS))
    ].copy()

    if df_len.empty:
        st.warning("No data available for this distance band.")
        continue

    fig = go.Figure()

    cycles = sorted(df_len["cycle_no"].unique())

    for rep in REPS:
        r = df_len[df_len["trial_id"] == rep].sort_values("cycle_no")

        push = r[r["metric_key"] == "push_length"]
        roll = r[r["metric_key"] == "rolling_length"]

        x_pos = np.array(push["cycle_no"]) + REP_OFFSET[rep]

        # ---- Push bar ----
        fig.add_bar(
            x=x_pos,
            y=push["value"],
            width=0.32,
            name=f"Push – {REP_LABELS[rep]}",
            marker_color=BAR_COLOURS["push_length"][rep],
        )

        # ---- Rolling bar (stacked) ----
        fig.add_bar(
            x=x_pos,
            y=roll["value"],
            width=0.32,
            base=push["value"],
            name=f"Rolling – {REP_LABELS[rep]}",
            marker_color=BAR_COLOURS["rolling_length"][rep],
        )

        # ---- Total cycle length line ----
        total = push["value"].values + roll["value"].values

        fig.add_scatter(
            x=x_pos,
            y=total + TEXT_OFFSET[rep],  # lift text to avoid overlap
            mode="lines+markers+text",
            name=f"Cycle Length – {REP_LABELS[rep]}",
            marker=dict(size=7, color=REP_COLOURS[rep]),
            line=dict(
                color=REP_COLOURS[rep],
                width=2,
                dash="solid" if rep == "60m_1" else "dash",
            ),
            text=[f"{v:.2f}" for v in total],
            textposition="top center",
            textfont=dict(size=10, color=REP_COLOURS[rep]),
        )

    # ---- Layout styling ----
    fig.update_layout(
        barmode="stack",
        template="simple_white",
        height=480,
        xaxis=dict(
            title="Cycle",
            tickmode="array",
            tickvals=cycles,
        ),
        yaxis=dict(
            title="Distance (m)",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=10),
        ),
        font=dict(color="#444"),
        margin=dict(l=50, r=30, t=40, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)
