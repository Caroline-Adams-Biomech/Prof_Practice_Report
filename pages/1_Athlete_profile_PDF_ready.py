# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


def render(pdf_mode=False):

    base_path = Path(__file__).resolve().parents[1]

    st.title("Track Testing: 60m Comparison")
    st.markdown("---")

    st.write("Simple test version (for debugging)")

    # -------------------------
    # Load data safely
    # -------------------------
    try:
        df = pd.read_excel(base_path / "data" / "60m_spatial_temporal.xlsx")
    except Exception as e:
        st.error(f"Data load failed: {e}")
        return

    trials = sorted(df["Trial"].dropna().unique())

    if pdf_mode:
        selected_trials = trials
    else:
        selected_trials = st.multiselect("Trials", trials, default=trials[:1])

    if not selected_trials:
        st.warning("Select at least one trial")
        return

    # -------------------------
    # Plot
    # -------------------------
    fig = go.Figure()

    for t in selected_trials:
        d = df[df["Trial"] == t]

        fig.add_trace(go.Scatter(
            x=d["Distance (m)"],
            y=d["Value"],
            mode="lines+markers",
            name=t
        ))

    if pdf_mode:
        st.image(fig.to_image(format="png"))
    else:
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render(pdf_mode=False)