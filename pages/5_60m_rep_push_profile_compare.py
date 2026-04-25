"""
Best 60 m Rep Push Profile – Rep Comparison
Author: Caroline Adams
"""

# =========================================================
# PAGE SETUP
# =========================================================
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# =========================================================
# LOGO
# =========================================================
logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"

if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

# =========================================================

# =========================================================
st.title("Best 60 m Push Profile – Rep Comparison")
st.write(
    "This page compares two best 60 m sprint repetitions. "
    "Results are shown for the early acceleration phase (0–10 m) "
    "and the maximum‑speed phase (35–45 m)."
)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    if not data_path.exists():
        st.error(f"Data file not found at: {data_path}")
        st.stop()

    df = pd.read_excel(data_path)

    # Normalise key fields (robust to Excel quirks)
    df["trial_id"] = (
        df["trial_id"]
        .astype(str)
        .str.strip()
        .str.replace(" ", "_", regex=False)
    )

    df["metric_key"] = df["metric_key"].astype(str).str.strip()

    df["distance_band"] = (
        df["distance_band"]
        .astype(str)
        .str.replace("–", "-", regex=False)
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
    "60m_1": "Best Rep 1",
    "60m_3": "Best Rep 2",
}

# =========================================================
# HELPER — REINDEX CYCLES (THIS IS THE KEY FIX)
# =========================================================
def reindex_cycles(df):
    """
    Convert absolute cycle_no to relative cycle index (1,2,3...)
    so reps can be compared visually.
    """
    df = df.sort_values("cycle_no").copy()
    df["cycle_idx"] = range(1, len(df) + 1)
    return df

# =========================================================
# SECTION 1 — AVERAGE CYCLE SPEED
# =========================================================
st.subheader("Average Cycle Speed")
st.write(
    "This shows speed per push cycle. Cycles are indexed relative to each rep, "
    "allowing a direct comparison of how speed builds and stabilises."
)

speed_max = df[df["metric_key"] == "cycle_av_speed"]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = px.line()

        for rep in REPS:
            rep_df = reindex_cycles(
                df[
                    (df["trial_id"] == rep)
                    & (df["distance_band"] == band)
                    & (df["metric_key"] == "cycle_av_speed")
                ]
            )

            fig.add_scatter(
                x=rep_df["cycle_idx"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
            )

        fig.update_layout(
            title=f"Average Cycle Speed ({band} m)",
            height=350,
            yaxis_range=[0, speed_max * 1.1],
            xaxis_title="Cycle",
            yaxis_title="Speed (m/s)",
            legend_title_text=""
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 2 — CYCLE LENGTH BREAKDOWN
# =========================================================
st.subheader("Cycle Length Breakdown")
st.write(
    "Stacked bars show how total cycle length is made up of push and rolling distance. "
    "Same colours represent the same phase; different shades distinguish reps."
)

rep_colours = {
    "60m_1": {"push_length": "#1f77b4", "rolling_length": "#aec7e8"},
    "60m_3": {"push_length": "#ff7f0e", "rolling_length": "#ffbb78"},
}

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = px.bar()

        for rep in REPS:
            rep_df = reindex_cycles(
                df[
                    (df["trial_id"] == rep)
                    & (df["distance_band"] == band)
                    & (df["metric_key"].isin(["push_length", "rolling_length"]))
                ]
            )

            for key in ["push_length", "rolling_length"]:
                sub_df = rep_df[rep_df["metric_key"] == key]

                fig.add_bar(
                    x=sub_df["cycle_idx"],
                    y=sub_df["value"],
                    name=f"{key.replace('_', ' ').title()} – {REP_LABELS[rep]}",
                    marker_color=rep_colours[rep][key],
                )

        fig.update_layout(
            title=f"Cycle Length ({band} m)",
            barmode="stack",
            height=350,
            yaxis_range=[0, 3],
            xaxis_title="Cycle",
            yaxis_title="Distance (m)",
            legend_title_text=""
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 3 — PUSH ANGLE
# =========================================================
st.subheader("Push Angle")
st.write(
    "This shows how push angle changes across cycles for each rep. "
    "Cycles are indexed relative to each rep to support direct comparison. "
    "The focus is on consistency, not on hitting a specific value."
)

angle_max = df[df["metric_key"] == "push_angle"]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = px.line()

        for rep in REPS:
            rep_df = reindex_cycles(
                df[
                    (df["trial_id"] == rep)
                    & (df["distance_band"] == band)
                    & (df["metric_key"] == "push_angle")
                ]
            )

            fig.add_scatter(
                x=rep_df["cycle_idx"],
                y=rep_df["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
            )

        fig.update_layout(
            title=f"Push Angle ({band} m)",
            height=350,
            yaxis_range=[0, angle_max * 1.1],
            xaxis_title="Cycle",
            yaxis_title="Angle (degrees)",
            legend_title_text=""
        )

        st.plotly_chart(fig, use_container_width=True)


