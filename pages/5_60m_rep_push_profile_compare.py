# coding: utf-8
"""
Best 60m Rep Push Profile – Rep Comparison
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(layout="wide")

# =========================================================
# LOGO
# =========================================================
logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=400)

# =========================================================
# TITLE / INTRO
# =========================================================
st.title("Best 60m Push Profile – Rep Comparison")
st.write(
    "This page compares two best 60 m sprint repetitions. Results are shown for the "
    "acceleration phase (0–10 m) and the maximum‑speed phase (35–45 m)."
)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    df = pd.read_excel(data_path)

    # Normalise key columns
    df["trial_id"] = df["trial_id"].astype(str).str.strip().str.replace(" ", "_", regex=False)
    df["metric_key"] = df["metric_key"].astype(str).str.strip()
    df["distance_band"] = df["distance_band"].astype(str).str.replace("–", "-", regex=False).str.strip()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df

df = load_data()

# =========================================================
# CONSTANTS
# =========================================================
DISTANCE_BANDS = ["0-10", "35-45"]
REPS = ["60m_1", "60m_3"]

REP_LABELS = {
    "60m_1": "Best Rep 1",
    "60m_3": "Best Rep 2",
}

LINE_STYLES = {
    "60m_1": dict(dash="solid"),
    "60m_3": dict(dash="dash"),
}

BAR_COLOURS = {
    "60m_1": {"push_length": "#1f77b4", "rolling_length": "#aec7e8"},
    "60m_3": {"push_length": "#ff7f0e", "rolling_length": "#ffbb78"},
}

# =========================================================
# HELPER — RELATIVE CYCLE INDEX
# =========================================================
def reindex_cycles(frame):
    frame = frame.sort_values("cycle_no").copy()
    frame["cycle_idx"] = range(1, len(frame) + 1)
    return frame

# =========================================================
# SECTION 1 — AVERAGE CYCLE SPEED
# =========================================================
st.subheader("Average Cycle Speed")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = px.line()

        for rep in REPS:
            rep_df = df[
                (df["trial_id"] == rep)
                & (df["distance_band"] == band)
                & (df["metric_key"] == "cycle_av_speed")
            ]

            if rep_df.empty:
                continue

            rep_df = reindex_cycles(rep_df)

            fig.add_scatter(
                x=rep_df["cycle_idx"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=LINE_STYLES[rep],
                marker=dict(size=7),
            )

        fig.update_layout(
            title=f"Average Cycle Speed ({band} m)",
            height=350,
            xaxis_title="Cycle",
            yaxis_title="Speed (m/s)",
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 2 — CYCLE LENGTH BREAKDOWN
# =========================================================
st.subheader("Cycle Length Breakdown")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = px.bar()

        for rep in REPS:
            rep_df = df[
                (df["trial_id"] == rep)
                & (df["distance_band"] == band)
                & (df["metric_key"].isin(["push_length", "rolling_length"]))
            ]

            if rep_df.empty:
                continue

            rep_df = reindex_cycles(rep_df)

            for key in ["push_length", "rolling_length"]:
                sub = rep_df[rep_df["metric_key"] == key]
                fig.add_bar(
                    x=sub["cycle_idx"],
                    y=sub["value"],
                    name=f"{key.replace('_',' ').title()} – {REP_LABELS[rep]}",
                    marker_color=BAR_COLOURS[rep][key],
                    offsetgroup=rep,
                    legendgroup=rep,
                )

        fig.update_layout(
            title=f"Cycle Length ({band} m)",
            barmode="stack",
            height=350,
            xaxis_title="Cycle",
            yaxis_title="Distance (m)",
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 3 — PUSH ANGLE
# =========================================================
st.subheader("Push Angle")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = px.line()

        for rep in REPS:
            rep_df = df[
                (df["trial_id"] == rep)
                & (df["distance_band"] == band)
                & (df["metric_key"] == "push_angle")
            ]

            if rep_df.empty:
                continue

            rep_df = reindex_cycles(rep_df)

            fig.add_scatter(
                x=rep_df["cycle_idx"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=LINE_STYLES[rep],
                marker=dict(size=7),
            )

        fig.update_layout(
            title=f"Push Angle ({band} m)",
            height=350,
            xaxis_title="Cycle",
            yaxis_title="Angle (degrees)",
        )

        st.plotly_chart(fig, use_container_width=True)
