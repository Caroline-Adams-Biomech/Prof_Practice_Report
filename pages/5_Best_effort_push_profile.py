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

logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"

# --- Logo centred at top
if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

# --- Page title & subtitle
st.title("Best Rep Push Profile")
st.write(
    "This page shows the metrics and push profile for your best rep, metrics are only provided for 0-10m and 35-45m due to the test setup and camera position."
    )


# -------------------------------------------------
# Load data from disk (FIXED PATH)
# -------------------------------------------------
@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    if not data_path.exists():
        st.error(f"Data file not found at: {data_path}")
        st.stop()

    return pd.read_excel(data_path)

# -------------------------------------------------
# Sidebar filters
# -------------------------------------------------
st.sidebar.header("Filters")

trial = st.sidebar.selectbox(
    "Trial",
    sorted(df["trial_id"].unique())
)

effort = st.sidebar.selectbox(
    "Effort type",
    sorted(df["effort_type"].unique())
)

distance_band = st.sidebar.selectbox(
    "Distance band",
    sorted(df["distance_band"].unique())
)

filtered = df[
    (df["trial_id"] == trial) &
    (df["effort_type"] == effort) &
    (df["distance_band"] == distance_band)
]

# -------------------------------------------------
# SECTION 1 — Cycle metrics table (wide)
# -------------------------------------------------
st.subheader(f"Cycle Metrics Table ({distance_band} m)")

table_df = (
    filtered
    .pivot_table(
        index="cycle_no",
        columns=["phase", "variable"],
        values="value"
    )
    .sort_index()
)

# Flatten column names for display
table_df.columns = [
    f"{phase} {var}".title()
    for phase, var in table_df.columns
]

st.dataframe(
    table_df.reset_index(),
    use_container_width=True
)

# -------------------------------------------------
# SECTION 2 — Average Cycle Velocity
# -------------------------------------------------
st.subheader("Average Cycle Velocity")

vel_df = filtered[
    (filtered["phase"] == "Cycle") &
    (filtered["variable"].isin(["avg_speed", "Average Speed", "average_speed"]))
]

fig_vel = px.line(
    vel_df,
    x="cycle_no",
    y="value",
    markers=True,
    labels={
        "cycle_no": "Cycle No.",
        "value": "Cycle Velocity (m/s)"
    },
    title=f"Average Cycle Velocity ({distance_band} m)"
)

fig_vel.update_traces(line_dash="dash")
fig_vel.update_layout(height=350)

st.plotly_chart(fig_vel, use_container_width=True)

# -------------------------------------------------
# SECTION 3 — Cycle length breakdown (Push / Rolling)
# -------------------------------------------------
st.subheader("Cycle Length Breakdown")

length_df = filtered[
    (filtered["variable"] == "length") &
    (filtered["phase"].isin(["Push", "Rolling", "Cycle"]))
]

fig_len = px.bar(
    length_df,
    x="cycle_no",
    y="value",
    color="phase",
    barmode="stack",
    labels={
        "cycle_no": "Cycle No.",
        "value": "Distance (m)"
    },
    title=f"Cycle Length Composition ({distance_band} m)"
)

fig_len.update_layout(height=350)

st.plotly_chart(fig_len, use_container_width=True)

# -------------------------------------------------
# SECTION 4 — Push vs Rolling time
# -------------------------------------------------
st.subheader("Push and Rolling Times")

time_df = filtered[
    (filtered["variable"] == "time") &
    (filtered["phase"].isin(["Push", "Rolling"]))
]

fig_time = px.line(
    time_df,
    x="cycle_no",
    y="value",
    color="phase",
    markers=True,
    labels={
        "cycle_no": "Cycle No.",
        "value": "Time (s)"
    },
    title=f"Push and Rolling Times ({distance_band} m)"
)

fig_time.update_layout(height=350)

st.plotly_chart(fig_time, use_container_width=True)


