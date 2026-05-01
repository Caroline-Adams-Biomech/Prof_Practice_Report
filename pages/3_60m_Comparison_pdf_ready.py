# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


def render(pdf_mode=False):

    # -----------------------------------------------------
    # Paths
    # -----------------------------------------------------
    base_path = Path(__file__).resolve().parents[1]

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------
    st.title("Track Testing: 60m Comparison")
    st.markdown("---")

    # -----------------------------------------------------
    # Metric definitions
    # -----------------------------------------------------
    st.subheader("Metric Definitions")

    if pdf_mode:
        st.write("⏱️ Interval Time = time per split")
        st.write("💨 Speed = distance / time")
    else:
        with st.popover("⏱️ Interval Time"):
            st.write("Time per split")
        with st.popover("💨 Speed"):
            st.write("Speed = distance / time")

    # -----------------------------------------------------
    # Load data
    # -----------------------------------------------------
    @st.cache_data
    def load_data():
        return pd.read_excel(base_path / "data" / "60m_spatial_temporal.xlsx")

    df = load_data()
    trials = sorted(df["Trial"].dropna().unique())

    # -----------------------------------------------------
    # Inputs
    # -----------------------------------------------------
    if pdf_mode:
        selected_trials = trials
    else:
        selected_trials = st.multiselect("Trials", trials, default=trials[:1])

    if len(selected_trials) == 0:
        st.warning("Select at least one trial")
        return

    # -----------------------------------------------------
    # Plot
    # -----------------------------------------------------
    fig = go.Figure()

    for t in selected_trials:
        d = df[df["Trial"] == t]
        fig.add_trace(go.Scatter(
            x=d["Distance (m)"],
            y=d["Value"],
            mode="lines+markers",
            name=t
        ))

    # -----------------------------------------------------
    # Display
    # -----------------------------------------------------
    if pdf_mode:
        st.image(fig.to_image(format="png"))
    else:
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # Table
    # -----------------------------------------------------
    st.subheader("Data")
    st.dataframe(df)


# ✅ THIS MAKES NORMAL PAGE WORK
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render(pdf_mode=False)
``