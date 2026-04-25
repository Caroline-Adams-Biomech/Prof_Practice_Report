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
    "This page shows push metrics from your best repetition. Results are shown for both the "
    "acceleration phase (0–10 m) and the maximum‑speed phase (35–45 m) of the sprint."
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

    # --- normalise distance labels
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
# SECTION 1 — Cycle Metrics Table 
# =========================================================
st.subheader("Cycle Metrics Table")

from decimal import Decimal, ROUND_HALF_UP

def round_half_up(value, decimals):
    if pd.isna(value):
        return value
    quant = Decimal("1") if decimals == 0 else Decimal(f"1.{'0' * decimals}")
    return float(Decimal(value).quantize(quant, rounding=ROUND_HALF_UP))

# build table using metric_key (matches Excel)
table_df = (
    df[df["distance_band"].isin(DISTANCE_BANDS)]
    .pivot_table(
        index=["distance_band", "cycle_no"],
        columns="metric_key",
        values="value"
    )
    .reset_index(drop=True)
)

# enforce exact column order (as requested)
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

# rename for athlete display
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

# formatting rules
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

# display table
st.dataframe(
    table_df,
    hide_index=True,
    use_container_width=False
)

# =========================================================
# SECTION — Average Cycle Speed
# =========================================================
st.markdown(
    "**Average Cycle Speed**  \n"
    "This shows how fast the chair is moving during each cycle. "
    "Comparing the two distances highlights how speed builds during acceleration "
    "and how well it is maintained at top speed."
)

speed_max = df[
    (df["variable"] == "cycle_av_speed")
]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):

    band_df = df[
        (df["distance_band"] == band)
        & (df["phase"] == "Cycle")
        & (df["variable"] == "cycle_av_speed")
    ]

    with col:
        fig = px.line(
            band_df,
            x="cycle_no",
            y="value",
            markers=True,
            title=f"Average Cycle Speed ({band} m)",
            labels={
                "cycle_no": "Cycle",
                "value": "Speed (m/s)"
            }
        )

        fig.update_layout(
            height=350,
            yaxis_range=[0, speed_max * 1.1]
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 3 — Cycle Length Breakdown
# =========================================================
st.markdown(
    "**Cycle Length**  \n"
    "Each bar shows how cycle length is made up of push distance and rolling distance. "
    "The dashed line shows total cycle length. In acceleration, longer cycle lengths usually "
    "come from a stronger or more effective push rather than longer rolling."
)

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_label = band

    bars_df = df[
        (df["distance_band"] == band_label)
        & (df["variable"] == "length")
        & (df["phase"].isin(["Push", "Rolling"]))
    ]

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
            title=f"Cycle Length ({band_label} m)",
            labels={"cycle_no": "Cycle", "value": "Distance (m)"}
        )

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

        fig.update_layout(height=350, yaxis_range=[0, 3])
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 4 — Push and Rolling Times
# =========================================================
st.markdown(
    "**Push and Rolling Time**  \n"
    "This shows how time is split between pushing and rolling in each cycle. "
    "Changes across cycles can help highlight fatigue, rhythm, or changes in strategy."
)

time_max = df[df["variable"] == "time"]["value"].max()

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    band_label = band

    band_df = df[
        (df["distance_band"] == band_label)
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
            title=f"Push & Rolling Time ({band_label} m)",
            labels={"cycle_no": "Cycle", "value": "Time (s)"}
        )

        fig.update_layout(height=350, yaxis_range=[0, time_max * 1.1])
        st.plotly_chart(fig, use_container_width=True)
