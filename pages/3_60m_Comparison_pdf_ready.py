# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


def render(pdf_mode=False):

    # =========================================================
    # PATHS
    # =========================================================
    base_path = Path(__file__).resolve().parents[1]
    logo_path = base_path / "images" / "Logo.png"

    # =========================================================
    # HEADER
    # =========================================================
    if logo_path.exists():
        st.image(str(logo_path), width=400)

    st.title("Track Testing : 60m Rep Comparison")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
    This page compares the four 60m sprint repetitions across key metrics.
    """)

    # =========================================================
    # METRIC DEFINITIONS
    # =========================================================
    st.subheader("Metric definitions")

    if pdf_mode:
        st.markdown("**⏱️ Interval Time:** Time taken per 10 m split")
        st.markdown("**💨 Speed:** Cycle length × frequency")
        st.markdown("**📏 Cycle Length:** Distance per push")
        st.markdown("**🔁 Frequency:** Cycles per second")
    else:
        with st.popover("⏱️ Interval Time"):
            st.write("Time taken per 10 m split")

        with st.popover("💨 Average Speed"):
            st.write("Speed = cycle length × frequency")

        with st.popover("📏 Cycle Length"):
            st.write("Distance per push cycle")

        with st.popover("🔁 Cycle Frequency"):
            st.write("Cycles per second")

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
    if pdf_mode:
        selected_trials = trial_names
    else:
        selected_trials = st.multiselect(
            "Trials",
            trial_names,
            default=trial_names[:1]
        )

    if not selected_trials:
        st.warning("Please select at least one trial")
        return

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

        fig.add_trace(
            go.Scatter(
                x=d["Distance (m)"],
                y=d["Value"],
                mode="lines+markers",
                name=trial
            )
        )

    # =========================================================
    # SHOW PLOT
    # =========================================================
    if pdf_mode:
        img = fig.to_image(format="png")
        st.image(img)
    else:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # =========================================================
    # TABLES
    # =========================================================
    st.subheader("All trials overview")

    for trial in trial_names:
        with st.expander(trial):
            tdf = df[df["Trial"] == trial]
            st.dataframe(tdf)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render(pdf_mode=False)