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
    "This page shows the push metrics from your best repetition. Results are shown for both "
    "the acceleration phase (0–10 m) and the maximum‑speed phase (35–45 m) of the sprint."
)

# =========================================================
# Load data
# =========================================================
@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    if not data_path.exists():
        st.error(f"Data file not found at: {data_path}")
        st.stop()

    df = pd.read_excel(data_path)

    # --- NORMALISE distance labels (dash vs en dash)
    df["distance_band"] = (
        df["distance_band"]
        .astype(str)
        .str.replace("–", "-", regex=False)
        .str.strip()
    )

    return df

df = load_data()

if df.empty:
    st.error("Loaded dataset is empty.")
    st.stop()

# =========================================================
# Distance bands (fixed, both shown everywhere)
# =========================================================
DISTANCE_BANDS = ["0-10", "35-45"]

# =========================================================
# SECTION 1 — Cycle metrics table (BOTH distance bands)
# =========================================================
st.subheader("Cycle Metrics Table")

table_df = (
    df[df["distance_band"].isin(DISTANCE_BANDS)]
    .pivot_table(
        index=["distance_band", "cycle_no"],
        columns=["phase", "variable"],
        values="value"
    )
    .sort_index()
)

# Flatten column names
table_df.columns = [
    f"{phase} {var}".title()
    for phase, var in table_df.columns
]

# Remove index so no line-number column appears
st.dataframe(
    table_df.reset_index(drop=True),
    use_container_width=True
)

# =========================================================
# SECTION 2 — Average Cycle Velocity (side‑by‑side)
# =========================================================
st.subheader("Average Cycle Velocity")

# find shared y-axis range
vel_max = df[
    (df["distance_band"].isin(DISTANCE_BANDS))
    & (df["phase"] == "Cycle")
    & (df["variable"].isin(["avg_speed", "Average Speed", "average_speed"]))
]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_df = df[
        (df["distance_band"] == band)
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
                "cycle_no": "Cycle",
                "value": "Speed (m/s)"
            },
            title=f"Average Cycle Velocity ({band} m)"
        )

        fig.update_layout(
            height=350,
            yaxis_range=[0, vel_max * 1.1]
        )

        st.plotly_chart(fig, use_container_width=True)
# =========================================================
# SECTION 3 — Cycle Length Breakdown
# =========================================================
st.subheader("Cycle Length Breakdown")

# shared y-axis range
length_max = (
    df[
        (df["distance_band"].isin(DISTANCE_BANDS))
        & (df["variable"] == "length")
    ]
    .groupby(["distance_band", "cycle_no"])["value"]
    .sum()
    .max()
)

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):

    # push + rolling bars
    bars_df = df[
        (df["distance_band"] == band)
        & (df["variable"] == "length")
        & (df["phase"].isin(["Push", "Rolling"]))
    ]

    # total cycle length line
    total_df = (
        bars_df
        .groupby("cycle_no", as_index=False)["value"]
        .sum()
        .rename(columns={"value": "cycle_length"})
    )

    with col:
        fig = px.bar(
            bars_df,
            x="cycle_no",
            y="value",
            color="phase",
            barmode="stack",
            labels={
                "cycle_no": "Cycle",
                "value": "Distance (m)"
            },
            title=f"Cycle Length ({band} m)"
        )

        # dashed total cycle length line
        fig.add_scatter(
            x=total_df["cycle_no"],
            y=total_df["cycle_length"],
            mode="lines+markers+text",
            name="Cycle Length",
            line=dict(color="black", dash="dash"),
            marker=dict(symbol="diamond", size=8),
            text=total_df["cycle_length"].round(2),
            textposition="top center"
        )

        fig.update_layout(
            height=350,
            yaxis_range=[0, length_max * 1.15],
            legend_title_text=""
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 4 — Push vs Rolling Time
# =========================================================
st.subheader("Push and Rolling Times")

time_max = df[
    (df["distance_band"].isin(DISTANCE_BANDS))
    & (df["variable"] == "time")
]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_df = df[
        (df["distance_band"] == band)
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
                "cycle_no": "Cycle",
                "value": "Time (s)"
            },
            title=f"Push & Rolling Time ({band} m)"
        )

        fig.update_layout(
            height=350,
            yaxis_range=[0, time_max * 1.1],
            legend_title_text=""
        )

        st.plotly_chart(fig, use_container_width=True)