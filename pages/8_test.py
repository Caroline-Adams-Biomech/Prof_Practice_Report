# coding: utf-8
"""
Best 60m Rep Push Profile – Rep Comparison (Plotly Faceted Version)
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(layout="wide")

# =========================================================
# COLOURS
# =========================================================
REP_COLOURS = {
    "60m_1": "#2ca02c",   # green
    "60m_3": "#46A9D6",   # light blue
}

BAR_COLOURS = {
    "push_length": {
        "60m_1": "#1f8f3a",
        "60m_3": "#1f6fae",
    },
    "rolling_length": {
        "60m_1": "#8fd19e",
        "60m_3": "#9ccfe8",
    },
}

REP_LABELS = {
    "60m_1": "Best Rep",
    "60m_3": "60m_3",
}

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(show_spinner=False)
def load_data():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "60m_push_breakdown.xlsx"

    df = pd.read_excel(data_path)

    df["trial_id"] = df["trial_id"].astype(str).str.strip()
    df["metric_key"] = df["metric_key"].astype(str).str.strip()
    df["distance_band"] = (
        df["distance_band"]
        .astype(str)
        .str.replace("–", "-", regex=False)
        .str.replace("−", "-", regex=False)
        .str.strip()
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


df = load_data()

# =========================================================
# TITLE
# =========================================================
st.title("Best 60m Push Profile – Rep Comparison")
st.write(
    "This section presents cycle length composition using stacked push and rolling "
    "distances, with total cycle length overlaid for each rep."
)

# =========================================================
# CYCLE LENGTH — FACETED PLOTLY VERSION
# =========================================================
st.subheader("Cycle Length Breakdown")

DISTANCE_BANDS = ["0-10", "35-45"]
REPS = ["60m_1", "60m_3"]

for band in DISTANCE_BANDS:

    st.markdown(f"**Cycle Length ({band} m)**")

    df_len = df[
        (df["metric_key"].isin(["push_length", "rolling_length"])) &
        (df["distance_band"] == band) &
        (df["trial_id"].isin(REPS))
    ].copy()

    if df_len.empty:
        st.warning("No data available for this distance band.")
        continue

    # ---- Compute total cycle length ----
    total = (
        df_len
        .groupby(["trial_id", "cycle_no"])["value"]
        .sum()
        .reset_index(name="cycle_length")
    )

    # ---- Base stacked bars using Plotly Express ----
    fig = px.bar(
        df_len,
        x="cycle_no",
        y="value",
        color="metric_key",
        facet_col="trial_id",
        color_discrete_map={
            "push_length": BAR_COLOURS["push_length"]["60m_1"],
            "rolling_length": BAR_COLOURS["rolling_length"]["60m_1"],
        },
    )

    # ---- Fix colours per facet (rep‑specific) ----
    for trace in fig.data:
        if trace.name == "push_length":
            trace.marker.color = [
                BAR_COLOURS["push_length"][rep] for rep in REPS
            ][trace.subplot[1] == "2"]
        elif trace.name == "rolling_length":
            trace.marker.color = [
                BAR_COLOURS["rolling_length"][rep] for rep in REPS
            ][trace.subplot[1] == "2"]

    # ---- Overlay total cycle length lines ----
    for i, rep in enumerate(REPS):
        t = total[total["trial_id"] == rep]

        fig.add_trace(
            go.Scatter(
                x=t["cycle_no"],
                y=t["cycle_length"],
                mode="lines+markers+text",
                text=[f"{v:.2f}" for v in t["cycle_length"]],
                textposition="top center",
                marker=dict(size=6, color=REP_COLOURS[rep]),
                line=dict(
                    width=2,
                    color=REP_COLOURS[rep],
                    dash="solid" if rep == "60m_1" else "dash",
                ),
                showlegend=False,
            ),
            row=1,
            col=i + 1,
        )

    # ---- Layout polish ----
    fig.update_layout(
        barmode="stack",
        template="simple_white",
        height=420,
        font=dict(color="#444"),
        xaxis_title="Cycle",
        yaxis_title="Distance (m)",
        legend_title_text="",
    )

    fig.for_each_annotation(lambda a: a.update(text=REP_LABELS[a.text]))

    st.plotly_chart(fig, use_container_width=True)