# -*- coding: utf-8 -*-
"""
Created on Fri May  1 13:18:32 2026

@author: Caroline Adams
"""

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

def render(pdf_mode=False):

    # =========================================================
    # TEXT FORMATTING
    # =========================================================
    st.markdown("""
    <style>
    .stApp { font-size: 19px; line-height: 1.55; }
    h1 { font-size: 42px; }
    h2 { font-size: 30px; }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # PATHS
    # =========================================================
    base_path = Path(__file__).resolve().parents[1]
    logo_path = base_path / "images" / "Logo.png"
    cycle_path = base_path / "images" / "cycle_definitions_image.png"

    if logo_path.exists():
        st.image(str(logo_path), width=400)

    st.title("Track Testing : 60m Rep Comparison")
    st.markdown("---")

    st.markdown("""
    This page compares the four 60m sprint repetitions...
    """)

    # =========================================================
    # METRIC DEFINITIONS
    # =========================================================
    st.write("### Metric definitions")

    # ✅ POPUP → STATIC TEXT SWITCH
    if pdf_mode:
        st.subheader("⏱️ Interval Time")
        st.write("Time taken across each 10m split")

        st.subheader("💨 Average Speed")
        st.write("Speed = cycle length × frequency")

        st.subheader("📏 Cycle Length")
        st.write("Distance covered per push cycle")

        st.subheader("🔁 Cycle Frequency")
        st.write("Pushes per second")
    else:
        with st.popover("⏱️ Interval Time"):
            st.write("Time taken across each 10m split")

        with st.popover("💨 Average Speed"):
            st.write("Speed = cycle length × frequency")

        with st.popover("📏 Cycle Length"):
            st.write("Distance covered per push cycle")

        with st.popover("🔁 Cycle Frequency"):
            st.write("Pushes per second")

    # =========================================================
    # LOAD DATA
    # =========================================================
    @st.cache_data
    def load():
        return pd.read_excel(base_path / "data" / "60m_spatial_temporal.xlsx")

    df = load()
    trial_names = sorted(df["Trial"].dropna().unique())

    # =========================================================
    # SELECTORS (disabled in PDF)
    # =========================================================
    if pdf_mode:
        selected_metric = "Average Speed (m/s)"
        selected_trials = trial_names
    else:
        selected_metric = st.selectbox("Metric", df["Metric"].unique())
        selected_trials = st.multiselect("Trials", trial_names, default=trial_names[:1])

    plot_df = df[df["Trial"].isin(selected_trials)]

    # =========================================================
    # PLOT
    # =========================================================
    fig = go.Figure()

    for trial in selected_trials:
        d = plot_df[plot_df["Trial"] == trial]
        fig.add_scatter(x=d["Distance (m)"], y=d["Value"], name=trial)

    # ✅ PLOT SWITCH
    if pdf_mode:
        st.image(fig.to_image(format="png"))
    else:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("All trials overview")
    for trial in trial_names:
        with st.expander(trial):
            st.dataframe(df[df["Trial"] == trial])


# ✅ REQUIRED
if __name__ == "__main__":
    render(pdf_mode=False)
``