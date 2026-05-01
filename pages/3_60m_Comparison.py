# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:53:25 2026
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go

# ✅ Page config (ONLY ONCE HERE)
st.set_page_config(layout="wide")

# =========================================================
# PATHS
# =========================================================
base_path = Path(__file__).resolve().parents[1]
logo_path = base_path / "images" / "Logo.png"
cycle_path = base_path / "images" / "cycle_definitions_image.png"

# =========================================================
# HEADER
# =========================================================
if logo_path.exists():
    st.image(str(logo_path), width=400)

st.title("Track Testing : 60m Rep Comparison")
st.markdown("---")

# =========================================================
# INTRO
# =========================================================
st.markdown("""
This page compares the four 60m sprint repetitions you completed across key metrics.
""")

# =========================================================
# METRIC DEFINITIONS
# =========================================================
st.subheader("Metric definitions")

with st.expander("⏱️ Interval Time (s)"):
    st.write("Time taken across each 10 m split.")

with st.expander("💨 Average Speed (m/s)"):
    st.write("Speed of athlete per split (m/s).")

with st.expander("📏 Average Cycle Length (m)"):
    st.write("Distance per push cycle.")

with st.expander("🔁 Average Cycle Frequency (CPS)"):
    st.write("Cycles per second.")

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    return pd.read_excel(base_path / "data" / "60m_spatial_temporal.xlsx")

df = load_data()
trial_names = sorted(df["Trial"].dropna().unique())

# =========================================================
# INPUTS
# =========================================================
selected_trials = st.multiselect(
    "Select trials",
    trial_names,
    default=trial_names[:1]
)

if not selected_trials:
    st.warning("Please select at least one trial.")
    st.stop()

# =========================================================
# FILTER DATA
# =========================================================
plot_df = df[df["Trial"].isin(selected_trials)]

# =========================================================
# PLOT
# =========================================================
fig = go.Figure()

for trial in selected_trials:
    d = plot_df[plot_df["Trial"] == trial]

    fig.add_trace(go.Scatter(
        x=d["Distance (m)"],
        y=d["Value"],
        mode="lines+markers",
        name=trial
    ))

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TABLES
# =========================================================
st.subheader("All trials overview")

for trial in trial_names:
    with st.expander(trial):
        st.dataframe(df[df["Trial"] == trial])