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
from decimal import Decimal, ROUND_HALF_UP

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
# TITLE / INTRO
# =========================================================
st.title("Best Rep Push Profile")
st.write(
    "This page shows push metrics from your best repetition. Results are shown "
    "for the early acceleration phase (0–10 m) and the maximum‑speed phase (35–45 m)."
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

    # normalise distance labels (hyphen vs en dash)
    df["distance_band"] = (
        df["distance_band"]
        .astype(str)
        .str.replace("–", "-", regex=False)
        .str.strip()
    )

    return df

df = load_data()

DISTANCE_BANDS = ["0-10", "35-45"]

# =========================================================
# ROUNDING HELPER (ROUND HALF UP)
# =========================================================
def round_half_up(value, decimals):
    if pd.isna(value):
        return value
    quant = Decimal("1") if decimals == 0 else Decimal("1." + "0" * decimals)
    return float(Decimal(value).quantize(quant, rounding=ROUND_HALF_UP))

# =========================================================
# SECTION 1 — CYCLE METRICS TABLE
# =========================================================
st.subheader("Cycle Metrics Table")

table_df = (
    df[df["distance_band"].isin(DISTANCE_BANDS)]
    .pivot_table(
        index=["distance_band", "cycle_no"],
        columns="metric_key",
        values="value"
    )
    .reset_index()  # KEEP cycle_no
)

desired_cols = [
    "cycle_no",
    "cycle_length",
    "push_length",
    "rolling_length",
    "cycle_freq",
    "push_time",
    "rolling_time",
    "push_angle",
    "cycle_av_speed",
]

table_df = table_df[[c for c in desired_cols if c in table_df.columns]]

table_df = table_df.rename(
    columns={
        "cycle_no": "Cycle Number",
        "cycle_length": "Cycle Length (m)",
        "push_length": "Push Length (m)",
        "rolling_length": "Rolling Length (m)",
        "cycle_freq": "Cycle Frequency (Hz)",
        "push_time": "Push Time (s)",
        "rolling_time": "Rolling Time (s)",
        "push_angle": "Push Angle (°)",
        "cycle_av_speed": "Average Cycle Speed (m/s)",
    }
)

# Formatting rules
table_df["Cycle Number"] = table_df["Cycle Number"].astype(int)
table_df["Push Angle (°)"] = table_df["Push Angle (°)"].apply(
    lambda x: round_half_up(x, 0)
)

cols_2dp = [
    "Cycle Length (m)",
    "Push Length (m)",
    "Rolling Length (m)",
    "Cycle Frequency (Hz)",
    "Push Time (s)",
    "Rolling Time (s)",
    "Average Cycle Speed (m/s)",
]

for col in cols_2dp:
    if col in table_df.columns:
        table_df[col] = table_df[col].apply(lambda x: round_half_up(x, 2))

st.dataframe(
    table_df,
    hide_index=True,
    use_container_width=False
)

# =========================================================
# SECTION 2 — AVERAGE CYCLE SPEED
# =========================================================
st.subheader("Average Cycle Speed")
st.write(
    "This shows how fast the chair is moving during each cycle. "
    "Comparing the two distances highlights how speed builds early "
    "and how well it is maintained later in the sprint."
)

speed_max = df[df["metric_key"] == "cycle_av_speed"]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_df = df[
        (df["distance_band"] == band)
        & (df["metric_key"] == "cycle_av_speed")
    ]

    with col:
        fig = px.line(
            band_df,
            x="cycle_no",
            y="value",
            markers=True,
            title=f"Average Cycle Speed ({band} m)",
            labels={"cycle_no": "Cycle", "value": "Speed (m/s)"}
        )

        fig.update_layout(height=350, yaxis_range=[0, speed_max * 1.1])
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 3 — CYCLE LENGTH BREAKDOWN
# =========================================================
st.subheader("Cycle Length Breakdown")
st.write(
    "The bars show how cycle length is made up of push distance and rolling distance. "
    "The dashed line shows total cycle length."
)

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    bars_df = df[
        (df["distance_band"] == band)
        & (df["metric_key"].isin(["push_length", "rolling_length"]))
    ]

    total_df = (
        bars_df
        .groupby("cycle_no", as_index=False)["value"]
        .sum()
    )

    with col:
        fig = px.bar(
            bars_df,
            x="cycle_no",
            y="value",
            color="metric_key",
            barmode="stack",
            title=f"Cycle Length ({band} m)",
            labels={"cycle_no": "Cycle", "value": "Distance (m)"}
        )

        fig.add_scatter(
            x=total_df["cycle_no"],
            y=total_df["value"],
            mode="lines+markers+text",
            line=dict(color="black", dash="dash"),
            text=total_df["value"].round(2),
            textposition="top center",
            name="Cycle Length"
        )

        fig.update_layout(height=350, yaxis_range=[0, 3])
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 4 — PUSH AND ROLLING TIMES
# =========================================================
st.subheader("Push and Rolling Time")
st.write(
    "This shows how time is split between pushing and rolling in each cycle. "
    "Changes across cycles can help highlight rhythm or fatigue."
)

time_max = df[df["metric_key"].isin(["push_time", "rolling_time"])]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    time_df = df[
        (df["distance_band"] == band)
        & (df["metric_key"].isin(["push_time", "rolling_time"]))
    ]

    with col:
        fig = px.line(
            time_df,
            x="cycle_no",
            y="value",
            color="metric_key",
            markers=True,
            title=f"Push & Rolling Time ({band} m)",
            labels={"cycle_no": "Cycle", "value": "Time (s)"}
        )

        fig.update_layout(height=350, yaxis_range=[0, time_max * 1.1])
        st.plotly_chart(fig, use_container_width=True)