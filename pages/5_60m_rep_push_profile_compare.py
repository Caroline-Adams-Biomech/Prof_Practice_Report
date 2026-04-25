# coding: utf-8
"""
Best 60m Rep Push Profile – Rep Comparison
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(layout="wide")

# =========================================================
# COLOURS
# =========================================================
# Rep colours (used in line plots)
REP_COLOURS = {
    "60m_1": "#2ca02c",   # green
    "60m_3": "#46A9D6",   # light blue
}

# Cycle length colours (push / rolling per rep)
CYCLE_COLOURS = {
    "60m_1": {
        "push_length": "#1f8f3a",      # dark green
        "rolling_length": "#8fd19e",   # light green
    },
    "60m_3": {
        "push_length": "#1f6fae",      # darker blue
        "rolling_length": "#9ccfe8",   # lighter blue
    },
}

# =========================================================
# LOGO
# =========================================================
logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=400)

# =========================================================
# TITLE
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

REP_LABELS = {
    "60m_1": "Best Rep",
    "60m_3": "60m_3",
}

# =========================================================
# SHARED PLOTLY STYLE
# =========================================================
def apply_plotly_style(fig):
    fig.update_layout(
        template="simple_white",
        font=dict(color="#444"),
        title_font=dict(size=14),
        legend=dict(frameon=False, font=dict(size=10)),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False),
    )
    return fig

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
                (df["trial_id"] == rep) &
                (df["distance_band"] == band) &
                (df["metric_key"] == "cycle_av_speed")
            ]

            if rep_df.empty:
                continue

            rep_df = rep_df.sort_values("cycle_no")
            rep_df["cycle_idx"] = range(1, len(rep_df) + 1)

            fig.add_scatter(
                x=rep_df["cycle_idx"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=dict(
                    color=REP_COLOURS[rep],
                    dash="solid" if rep == "60m_1" else "dash",
                    width=2,
                ),
                marker=dict(size=6, color=REP_COLOURS[rep]),
            )

        fig.update_layout(
            title=f"Average Cycle Speed ({band} m)",
            xaxis_title="Cycle",
            yaxis_title="Speed (m/s)",
        )

        st.plotly_chart(apply_plotly_style(fig), use_container_width=True)

# =========================================================
# SECTION 2 — CYCLE LENGTH BREAKDOWN (MATPLOTLIB)
# =========================================================
st.subheader("Cycle Length Breakdown")

plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "none",
    "axes.facecolor": "white",
    "axes.labelcolor": "#444",
    "xtick.color": "#444",
    "ytick.color": "#444",
    "grid.color": "#dddddd",
    "font.size": 11,
})

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        df_len = df[
            (df["distance_band"] == band) &
            (df["metric_key"].isin(["push_length", "rolling_length"])) &
            (df["trial_id"].isin(REPS))
        ]

        if df_len.empty:
            continue

        cycles = sorted(df_len["cycle_no"].unique())
        x = np.arange(len(cycles))
        width = 0.35

        fig, ax = plt.subplots(figsize=(7, 4))

        for i, rep in enumerate(REPS):
            r = df_len[df_len["trial_id"] == rep]

            push = (
                r[r["metric_key"] == "push_length"]
                .sort_values("cycle_no")["value"].values
            )

            roll = (
                r[r["metric_key"] == "rolling_length"]
                .sort_values("cycle_no")["value"].values
            )

            ax.bar(
                x + (i - 0.5) * width,
                push,
                width,
                label=f"Push – {REP_LABELS[rep]}",
                color=CYCLE_COLOURS[rep]["push_length"],
            )

            ax.bar(
                x + (i - 0.5) * width,
                roll,
                width,
                bottom=push,
                label=f"Rolling – {REP_LABELS[rep]}",
                color=CYCLE_COLOURS[rep]["rolling_length"],
            )

        ax.set_title(f"Cycle Length ({band} m)")
        ax.set_xlabel("Cycle")
        ax.set_ylabel("Distance (m)")
        ax.set_xticks(x)
        ax.set_xticklabels(cycles)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(frameon=False, fontsize=9)

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
                (df["trial_id"] == rep) &
                (df["distance_band"] == band) &
                (df["metric_key"] == "push_angle")
            ]

            if rep_df.empty:
                continue

            rep_df = rep_df.sort_values("cycle_no")
            rep_df["cycle_idx"] = range(1, len(rep_df) + 1)

            fig.add_scatter(
                x=rep_df["cycle_idx"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=dict(
                    color=REP_COLOURS[rep],
                    dash="solid" if rep == "60m_1" else "dash",
                    width=2,
                ),
                marker=dict(size=6, color=REP_COLOURS[rep]),
            )

        fig.update_layout(
            title=f"Push Angle ({band} m)",
            xaxis_title="Cycle",
            yaxis_title="Angle (degrees)",
        )

        st.plotly_chart(apply_plotly_style(fig), use_container_width=True)