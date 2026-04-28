# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:53:25 2026
@author: Caroline Adams
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import math

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Track Testing 60m reps",
    layout="wide"
)
# =========================================================
#PLot width settings
# =========================================================
def plot_container_start(max_width_px=1150):
    st.markdown(
        f"""
        <div style="
            max-width:{max_width_px}px;
            margin-left:auto;
            margin-right:auto;
        ">
        """,
        unsafe_allow_html=True
    )

def plot_container_end():
    st.markdown("</div>", unsafe_allow_html=True)
# =========================================================
# =========================================================
# TEXT & UI FORMATTING (SUGGESTION 1 + 3)
# =========================================================
# =========================================================
# TEXT FORMATTING (INCREASED LEGIBILITY)
# =========================================================
st.markdown(
    """
    <style>
    /* Base application text */
    .stApp {
        font-size: 19px;
        line-height: 1.55;
    }

    /* Page title (st.title) */
    h1 {
        font-size: 42px;
        margin-bottom: 0.6em;
    }

    /* Section headers (st.subheader) */
    h2 {
        font-size: 30px;
        margin-top: 1.4em;
        margin-bottom: 0.4em;
    }

    /* Sub-section headers (####) */
    h4 {
        font-size: 24px;
        margin-top: 1.2em;
        margin-bottom: 0.3em;
    }

    /* Widget labels (selectbox, multiselect, toggles) */
    label {
        font-size: 18px !important;
    }

    /* Dropdown / multiselect selected values */
    div[data-baseweb="select"] {
        font-size: 18px;
    }

    /* Toggle labels */
    span[data-testid="stMarkdownContainer"] {
        font-size: 18px;
    }

    /* Captions and helper text */
    .stCaption {
        font-size: 16px;
        line-height: 1.4;
    }

    /* Multiselect pills – toned down but readable */
    span[data-baseweb="tag"] {
        background-color: #f2f2f2 !important;
        color: #333 !important;
        font-size: 16px;
        border-radius: 8px;
        padding: 4px 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# PATHS & IMAGES
# =========================================================
base_path = Path(__file__).resolve().parents[1]
logo_path = base_path / "images" / "Logo.png"
cycle_path = base_path / "images" / "cycle_definitions_image.png"

# =========================================================
# HEADER
# =========================================================
if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

st.title("Track Testing 60m reps")

st.markdown(
    """
    <p style="font-size:18px;">
    This page compares the four 60m sprint repetitions you completed, focusing on key
    performance metrics across 10&nbsp;m splits.<br><br>
    When looking at these graphs, we are interested in the <strong>shape of the profiles</strong>
    rather than individual values. The shape represents your individual <strong>push signature</strong>.
    Exact numerical values for each metric and split are provided in the
    <strong>tables at the bottom of the page</strong> for detailed reference.
    </p>
    """,
    unsafe_allow_html=True
)

# =========================================================
# METRIC DEFINITIONS
# =========================================================
st.write("### Metric definitions")

with st.popover("⏱️ Interval Time (s)"):
    st.subheader("⏱️ Interval Time (seconds)")
    st.write("Time taken to travel from the start to the end of each 10 m split.")

with st.popover("💨 Average Speed (m/s)"):
    st.subheader("💨 Average Speed (m/s)")
    st.write("The average speed of the athlete and chair during each 10 m split.")

with st.popover("🔂📏 Average Cycle Length (m)"):
    st.subheader("🔂📏 Average Cycle Length (m)")
    st.markdown(
        """
        The average distance travelled during one cycle within each 10 m split.

        One **cycle** consists of:
        - the ***push phase*** (hands in contact with the push rim)
        - the ***rolling phase*** (hands off the rim while the chair freewheels)
        """
    )
    if cycle_path.exists():
        st.image(
            str(cycle_path),
            caption="Push phase + rolling phase together make one cycle",
            use_container_width=True,
        )

with st.popover("🔁 Average Cycle Frequency (CPS)"):
    st.subheader("🔁 Average Cycle Frequency (Cycles per Second)")
    st.write("The average number of cycles per second — a cadence measure.")

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_sprint_data():
    return pd.read_excel(
        base_path / "data" / "60m_spatial_temporal.xlsx",
        sheet_name=0
    )

df = load_sprint_data()
trial_names = sorted(df["Trial"].dropna().unique())

# =========================================================
# METRIC MAP
# =========================================================
METRIC_MAP = {
    "Interval Time (s)": "Interval Time (s)",
    "Average Speed (m/s)": "Average Velocity (m/s)",
    "Average Cycle Length (m)": "Average Cycle Length (m)",
    "Average Cycle Frequency (CPS)": "Average Cycle Frequency (Hz)",
}

# =========================================================
# COLOUR MAP
# =========================================================
colour_map = {
    "60m_1": "#2ca02c",
    "60m_2": "#2745C8",
    "60m_3": "#46A9D6",
    "60m_4": "#9D32BE",
}

# =========================================================
# SECTION: REP PROFILES
# =========================================================
st.subheader("60m Rep profiles")

st.markdown(
    """
    <p style="font-size:18px;">
    Select a <strong>metric of interest</strong> and the trials you wish to view.
    You can explore variability between repetitions or compare one repetition
    directly against your <strong>best rep</strong>.
    </p>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# WHAT TO PLOT
# -----------------------------
st.markdown("#### What to plot")

selected_metric = st.selectbox("Metric to plot", list(METRIC_MAP.keys()))
metric_key = METRIC_MAP[selected_metric]
metric_all_df = df[df["Metric"] == metric_key]

means = metric_all_df.groupby("Trial")["Value"].mean()
best_trial = means.idxmin() if selected_metric == "Interval Time (s)" else means.idxmax()
best_desc = "lowest average interval time" if selected_metric == "Interval Time (s)" else "highest average value"

selected_trials = st.multiselect("Trials of interest", trial_names, default=trial_names[:1])
if not selected_trials:
    st.warning("Please select at least one trial.")
    st.stop()

# -----------------------------
# ANALYSIS OPTIONS (SUGGESTION 2)
# -----------------------------
st.markdown(
    """
    <div style="margin-top:1.2em; padding-top:0.5em; border-top:1px solid #ddd;">
    <h4>Analysis options</h4>
    </div>
    """,
    unsafe_allow_html=True
)

show_minmax = st.toggle("Show min–max range across all reps")

compare_to_best = st.toggle("Compare one other rep to your best")
if compare_to_best:
    st.caption("Best rep is recalculated separately for each metric.")
    comparison_trial = st.selectbox(
        "Rep to compare against best",
        [t for t in trial_names if t != best_trial]
    )
    display_trials = [best_trial, comparison_trial]
    show_minmax = False
else:
    display_trials = selected_trials

# =========================================================
# FILTER DATA FOR PLOTTING
# =========================================================
plot_df = df[(df["Trial"].isin(display_trials)) & (df["Metric"] == metric_key)]

# =========================================================
# BREATHING ROOM + BEST REP DISPLAY (SUGGESTION 4)
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
st.info(f"⭐ **Best rep:** {best_trial} ({best_desc})")

# =========================================================
# MIN–MAX BAND
# =========================================================
range_df = (
    metric_all_df.groupby("Distance (m)")
    .agg(min_val=("Value", "min"), max_val=("Value", "max"))
    .reset_index()
)

# =========================================================
# PLOT
# =========================================================
fig = go.Figure()

if show_minmax:
    fig.add_trace(
        go.Scatter(
            x=list(range_df["Distance (m)"]) + list(range_df["Distance (m)"][::-1]),
            y=list(range_df["max_val"]) + list(range_df["min_val"][::-1]),
            fill="toself",
            fillcolor="rgba(190,190,190,0.4)",
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            name="Min–max range"
        )
    )

for trial in display_trials:
    d = plot_df[plot_df["Trial"] == trial]
    fig.add_trace(
        go.Scatter(
            x=d["Distance (m)"],
            y=d["Value"],
            mode="lines+markers",
            name=f"★ Best rep ({best_trial})" if trial == best_trial else trial,
            line=dict(color=colour_map[trial], width=2),
            marker=dict(size=7)
        )
    )

fig.update_layout(
    template="simple_white",
    height=520,
    hovermode="x unified",
    margin=dict(l=60, r=40, t=40, b=60),

    font=dict(
        size=16
    ),
    xaxis=dict(
        title="Distance (m)",
        range=[-2, 65],
        dtick=10,
        showgrid=False,   # ✅ remove gridlines
        showline=True,
        linecolor="black",
        linewidth=1,
        ticks="outside",
        tickfont=dict(size=15),
        title_font=dict(size=16),
        zeroline=False,
    ),
    yaxis=dict(
        title=selected_metric,
        showgrid=False,   # ✅ remove gridlines
        showline=True,
        linecolor="black",
        linewidth=1,
        ticks="outside",
        tickfont=dict(size=15),
        title_font=dict(size=16),
        zeroline=False,
        ),
    legend=dict(
        font=dict(size=14),
        borderwidth=0
    ),
)

plot_container_start(1150)
st.plotly_chart(fig, use_container_width=True)
plot_container_end()

# =========================================================
# ALL TRIALS OVERVIEW TABLES
# =========================================================
st.subheader("All trials overview")

for trial in trial_names:
    with st.expander(trial):
        tdf = df[df["Trial"] == trial]
        table = tdf.pivot(index="Metric", columns="Distance (m)", values="Value")
        table = table.loc[:, table.columns > 10]
        table.columns = [f"{int(c-10)}–{int(c)} m" for c in table.columns]
        st.dataframe(table.round(2), use_container_width=True)