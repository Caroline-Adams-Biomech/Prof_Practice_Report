# coding: utf-8
"""
Best 60m Rep Push Profile – Rep Comparison (Plotly Faceted Version)
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# CYCLE LENGTH — FACETED PLOTLY VERSION
# =========================================================
# =========================================================
# SECTION — CYCLE LENGTH BREAKDOWN (PLOTLY, FACETED BY REP)
# =========================================================
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.subheader("Cycle Length Breakdown")

DISTANCE_BANDS = ["0-10", "35-45"]
REPS = ["60m_1", "60m_3"]

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

    # -----------------------------------------------------
    # Create subplot layout (one column per rep)
    # -----------------------------------------------------
    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        subplot_titles=[REP_LABELS[r] for r in REPS],
    )

    # -----------------------------------------------------
    # Add traces per rep
    # -----------------------------------------------------
    for col, rep in enumerate(REPS, start=1):

        r = df_len[df_len["trial_id"] == rep].sort_values("cycle_no")

        push = r[r["metric_key"] == "push_length"]
        roll = r[r["metric_key"] == "rolling_length"]

        cycles = push["cycle_no"]

        # ---- Push bar ----
        fig.add_bar(
            x=cycles,
            y=push["value"],
            name="Push",
            marker_color=BAR_COLOURS["push_length"][rep],
            row=1,
            col=col,
            showlegend=(col == 1),
        )

        # ---- Rolling bar (stacked) ----
        fig.add_bar(
            x=cycles,
            y=roll["value"],
            name="Rolling",
            marker_color=BAR_COLOURS["rolling_length"][rep],
            row=1,
            col=col,
            showlegend=(col == 1),
        )

        # ---- Total cycle length line ----
        total = (
            push.set_index("cycle_no")["value"]
            + roll.set_index("cycle_no")["value"]
        )

        fig.add_scatter(
            x=total.index,
            y=total.values,
            mode="lines+markers+text",
            text=[f"{v:.2f}" for v in total.values],
            textposition="top center",
            marker=dict(
                size=7,
                color=REP_COLOURS[rep],
            ),
            line=dict(
                width=2,
                color=REP_COLOURS[rep],
                dash="solid" if rep == "60m_1" else "dash",
            ),
            name="Cycle Length",
            showlegend=(col == 1),
            row=1,
            col=col,
        )

    # -----------------------------------------------------
    # Layout styling
    # -----------------------------------------------------
    fig.update_layout(
        barmode="stack",
        template="simple_white",
        height=440,
        font=dict(color="#444"),
        yaxis_title="Distance (m)",
        xaxis_title="Cycle",
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=10),
        ),
        margin=dict(t=50, l=50, r=30, b=40),
    )

    fig.for_each_annotation(lambda a: a.update(font=dict(size=12)))

    st.plotly_chart(fig, use_container_width=True)
