# coding: utf-8
"""
Best 60m Rep Push Profile – Rep Comparison
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
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

TIME_COLOURS = {
    "push_time": "#444444",
    "rolling_time": "#999999",
}

REP_LABELS = {
    "60m_1": "Best Rep",
    "60m_3": "60m 3",
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
# CONSTANTS
# =========================================================
DISTANCE_BANDS = ["0-10", "35-45"]
REPS = ["60m_1", "60m_3"]

REP_OFFSET = {"60m_1": -0.18, "60m_3": 0.18}

Y_MAX = 3.5
TEXT_SIZE = 14
TEXT_PAD = 0.22

# =========================================================
# TITLE
# =========================================================
st.title("Best 60m Push Profile – Rep Comparison")
st.write(
    "This page compares two best 60 m sprint repetitions across the "
    "acceleration (0–10 m) and maximum‑speed (35–45 m) phases."
)

# =========================================================
# SECTION 1 — AVERAGE CYCLE SPEED
# =========================================================
st.subheader("Average Cycle Speed")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = go.Figure()

        for rep in REPS:
            rep_df = df[
                (df["trial_id"] == rep) &
                (df["distance_band"] == band) &
                (df["metric_key"] == "cycle_av_speed")
            ].sort_values("cycle_no")

            if rep_df.empty:
                continue

            fig.add_scatter(
                x=rep_df["cycle_no"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=dict(
                    color=REP_COLOURS[rep],
                    width=2,
                    dash="solid" if rep == "60m_1" else "dash",
                ),
                marker=dict(size=6),
            )

        fig.update_layout(
            title=f"Average Cycle Speed ({band} m)",
            xaxis_title="Cycle",
            yaxis_title="Speed (m/s)",
            template="simple_white",
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 2 — CYCLE LENGTH BREAKDOWN (FINAL PLOTLY VERSION)
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
                y=total,
                mode="lines+markers",
                marker=dict(size=7, color=REP_COLOURS[rep]),
                line=dict(
                    color=REP_COLOURS[rep],
                    width=2,
                    dash="solid" if rep == "60m_1" else "dash",
                ),
                showlegend=False,
            )

            fig.add_scatter(
                x=x,
                y=total + TEXT_PAD,
                mode="text",
                text=[f"{v:.2f}" for v in total],
                textfont=dict(size=TEXT_SIZE, color=REP_COLOURS[rep]),
                textposition="top center",
                showlegend=False,
            )

        fig.update_layout(
            title=f"Cycle Length ({band} m)",
            height=420,
            barmode="stack",
            template="simple_white",
            yaxis=dict(range=[0, Y_MAX]),
            xaxis=dict(tickmode="array", tickvals=cycles),
            margin=dict(t=90),
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 3 — PUSH ANGLE
# =========================================================
st.subheader("Push Angle")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = go.Figure()

        for rep in REPS:
            rep_df = df[
                (df["trial_id"] == rep) &
                (df["distance_band"] == band) &
                (df["metric_key"] == "push_angle")
            ].sort_values("cycle_no")

            if rep_df.empty:
                continue

            fig.add_scatter(
                x=rep_df["cycle_no"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=dict(
                    color=REP_COLOURS[rep],
                    width=2,
                    dash="solid" if rep == "60m_1" else "dash",
                ),
                marker=dict(size=6),
            )

        fig.update_layout(
            title=f"Push Angle ({band} m)",
            xaxis_title="Cycle",
            yaxis_title="Angle (degrees)",
            template="simple_white",
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 4 — PUSH AND ROLLING TIME
# =========================================================
st.subheader("Push and Rolling Time")
st.write(
    "This shows how time is split between pushing and rolling in each cycle. "
    "Changes across cycles can help highlight rhythm or fatigue."
)

time_max = df[df["metric_key"].isin(["push_time", "rolling_time"])]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = go.Figure()

        for metric in ["push_time", "rolling_time"]:
            metric_df = df[
                (df["distance_band"] == band) &
                (df["metric_key"] == metric)
            ].sort_values("cycle_no")

            fig.add_scatter(
                x=metric_df["cycle_no"],
                y=metric_df["value"],
                mode="lines+markers",
                name=metric.replace("_", " ").title(),
                line=dict(width=2),
                marker=dict(size=6),
            )

        fig.update_layout(
            title=f"Push & Rolling Time ({band} m)",
            xaxis_title="Cycle",
            yaxis_title="Time (s)",
            yaxis=dict(range=[0, time_max * 1.1]),
            template="simple_white",
        )

        st.plotly_chart(fig, use_container_width=True)