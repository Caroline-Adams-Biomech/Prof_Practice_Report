# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:38:52 2026

@author: Caroline Adams
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
# Logo
# =========================================================
logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"

if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

# =========================================================
# Page title / intro
# =========================================================
st.title("Best Rep Push Profile")
st.write(
    "This page shows the metrics and push profile for your best repetition. "
    "Metrics are provided for the acceleration phase (0–10 m) and maximum‑velocity "
    "phase (35–45 m) due to the test setup and camera positioning."
)

# =========================================================
# Load data from disk
# =========================================================
@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    if not data_path.exists():
        st.error(f"Data file not found at: {data_path}")
        st.stop()

    return pd.read_excel(data_path)

df = load_data()

if df.empty:
    st.error("Loaded dataset is empty.")
    st.stop()

# =========================================================
# Sidebar filters (trial & effort only)
# =========================================================
st.sidebar.header("Filters")

trial = st.sidebar.selectbox(
    "Trial",
    sorted(df["trial_id"].dropna().unique())
)

effort = st.sidebar.selectbox(
    "Effort type",
    sorted(df["effort_type"].dropna().unique())
)

# distance bands are FIXED for this page
DISTANCE_BANDS = ["0–10", "35–45"]

# =========================================================
# SECTION 1 — Cycle metrics table (wide, per distance band)
# =========================================================
st.subheader("Cycle Metrics Table")

band_for_table = st.radio(
    "Select distance band",
    DISTANCE_BANDS,
    horizontal=True
)

filtered = df[
    (df["trial_id"] == trial)
    & (df["effort_type"] == effort)
    & (df["distance_band"] == band_for_table)
]

table_df = (
    filtered
    .pivot_table(
        index="cycle_no",
        columns=["phase", "variable"],
        values="value"
    )
    .sort_index()
)

# Flatten column names for clean display
table_df.columns = [
    f"{phase} {var}".title()
    for phase, var in table_df.columns
]

st.dataframe(
    table_df.reset_index(),
    use_container_width=True
)

# =========================================================
# SECTION 2 — Average Cycle Velocity (side‑by‑side)
# =========================================================
st.subheader("Average Cycle Velocity")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_df = df[
        (df["trial_id"] == trial)
        & (df["effort_type"] == effort)
        & (df["distance_band"] == band)
        & (df["phase"] == "Cycle")
        & (df["variable"].isin(["avg_speed", "Average Speed", "average_speed"]))
    ]

    with col:
        fig = px.line(
            band_df,
            x="cycle_no",
            y="value",
            markers=True,
            labels={
                "cycle_no": "Cycle No.",
                "value": "Cycle Velocity (m/s)"
            },
            title=f"Average Cycle Velocity ({band} m)"
        )

        fig.update_traces(line_dash="dash")
        fig.update_layout(height=350)

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 3 — Cycle Length Breakdown (Push + Rolling)
# =========================================================
st.subheader("Cycle Length Breakdown")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_df = df[
        (df["trial_id"] == trial)
        & (df["effort_type"] == effort)
        & (df["distance_band"] == band)
        & (df["variable"] == "length")
        & (df["phase"].isin(["Push", "Rolling"]))
    ]

    with col:
        fig = px.bar(
            band_df,
            x="cycle_no",
            y="value",
            color="phase",
            barmode="stack",
            labels={
                "cycle_no": "Cycle No.",
                "value": "Distance (m)"
            },
            title=f"Cycle Length ({band} m)"
        )

        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 4 — Push vs Rolling Time
# =========================================================
st.subheader("Push and Rolling Times")

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_df = df[
        (df["trial_id"] == trial)
        & (df["effort_type"] == effort)
        & (df["distance_band"] == band)
        & (df["variable"] == "time")
        & (df["phase"].isin(["Push", "Rolling"]))
    ]

    with col:
        fig = px.line(
            band_df,
            x="cycle_no",
            y="value",
            color="phase",
            markers=True,
            labels={
                "cycle_no": "Cycle No.",
                "value": "Time (s)"
            },
            title=f"Push & Rolling Times ({band} m)"
        )

        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)