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
@st.cache_data(show_spinner=False)
def load_data():

    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    df = pd.read_excel(data_path)

    # --- Normalise identifiers ---
    df["trial_id"] = df["trial_id"].astype(str).str.strip()
    df["metric_key"] = df["metric_key"].astype(str).str.strip()

    # --- CRITICAL: normalise unicode dashes in distance band ---
    df["distance_band"] = (
        df["distance_band"]
        .astype(str)
        .str.replace("–", "-", regex=False)   # en-dash
        .str.replace("−", "-", regex=False)   # minus
        .str.strip()
    )

    # --- Ensure values are numeric ---
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


# ✅ REQUIRED: call the loader
df = load_data()


# =========================================================
# CONSTANTS
# =========================================================
DISTANCE_BANDS = ["0-10", "35-45"]
REPS = ["60m_1", "60m_3"]

REP_LABELS = {
    "60m_1": "Best Rep",
    "60m_3": "60m_3",
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
# =========================================================
# SECTION 2 — CYCLE LENGTH BREAKDOWN (GROUPED STACKS)
# =========================================================
st.subheader("Cycle Length Breakdown")

import matplotlib.pyplot as plt
import numpy as np

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:

        # Filter once per panel
        df_len = df[
            (df["distance_band"] == band) &
            (df["metric_key"].isin(["push_length", "rolling_length"])) &
            (df["trial_id"].isin(REPS))
        ]

        if df_len.empty:
            st.warning("No data available for this distance band.")
            continue

        reps = REPS
        width = 0.35

        # Unique cycles (use cycle_no directly)
        cycles = sorted(df_len["cycle_no"].unique())
        x = np.arange(len(cycles))

        fig, ax = plt.subplots(figsize=(7, 4))

        for i, rep in enumerate(reps):
            r = df_len[df_len["trial_id"] == rep]

            push = (
                r[r["metric_key"] == "push_length"]
                .sort_values("cycle_no")["value"]
                .values
            )

            roll = (
                r[r["metric_key"] == "rolling_length"]
                .sort_values("cycle_no")["value"]
                .values
            )

            ax.bar(
                x + (i - 0.5) * width,
                push,
                width,
                label=f"Push – {REP_LABELS[rep]}",
                color=BAR_COLOURS[rep]["push_length"]
            )

            ax.bar(
                x + (i - 0.5) * width,
                roll,
                width,
                bottom=push,
                label=f"Rolling – {REP_LABELS[rep]}",
                color=BAR_COLOURS[rep]["rolling_length"]
            )

        # Formatting
        ax.set_title(f"Cycle Length ({band} m)")
        ax.set_xlabel("Cycle")
        ax.set_ylabel("Distance (m)")
        ax.set_xticks(x)
        ax.set_xticklabels(cycles)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)

        plt.tight_layout()
        st.pyplot(fig)
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
