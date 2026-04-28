

# coding: utf-8
"""
Best 60m Rep Push Profile – Rep Comparison
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Athlete Profile",
    layout="wide"
)
# =========================================================
# PAGE SETUP
# =========================================================

logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"

# --- Logo centred at top
if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

# =========================================================

# paths for images
base_path = Path(__file__).resolve().parents[1]
cycle_path = base_path / "images" / "cycle_definitions_image.png"
pushangle_path = base_path / "images" / "push_angle.png"

# =========================================================
# COLOURS
# =========================================================
REP_COLOURS = {
    "60m_1": "#2ca02c",
    "60m_3": "#46A9D6",
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
    "60m_3": "Rep 3",
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
# CONSTANTS
# =========================================================
DISTANCE_BANDS = ["0-10", "35-45"]
REP_OFFSET = {"60m_1": -0.18, "60m_3": 0.18}

TEXT_SIZE = 14
TEXT_PAD = 0.22


# =========================================================
# TITLE
# =========================================================
st.title("60m Push Profile")
st.write(
    """
    This page shows push metrics from your fastest 60m repetition and Rep 3 your 3rd fastest Rep if selected. Based on the camera setup the metrics provided are for the initial acceleration (0–10 m) and the higher speed phase (35–45 m).
    """
)
# =========================================================
# REP SELECTION
# =========================================================
st.subheader("Rep Selection")
show_rep_3 = st.checkbox("To include Rep 3 for a comparison click here", value=True)

REPS = ["60m_1"]
if show_rep_3:
    REPS.append("60m_3")
# =========================================================
# PRE‑COMPUTE GLOBAL Y‑AXES (KEY CHANGE)
# =========================================================

# --- Average cycle speed ---
GLOBAL_SPEED_MAX = (
    df[
        (df["metric_key"] == "cycle_av_speed")
        & (df["trial_id"].isin(REPS))
    ]["value"].max() * 1.1
)

# --- Push angle ---
GLOBAL_ANGLE_MAX = (
    df[
        (df["metric_key"] == "push_angle")
        & (df["trial_id"].isin(REPS))
    ]["value"].max() * 1.1
)

# --- Cycle length (push + rolling) ---
cycle_totals = (
    df[
        (df["metric_key"].isin(["push_length", "rolling_length"]))
        & (df["trial_id"].isin(REPS))
    ]
    .groupby(["trial_id", "distance_band", "cycle_no"])["value"]
    .sum()
)
GLOBAL_CYCLE_MAX = cycle_totals.max() * 1.1

# --- Push & rolling time ---
GLOBAL_TIME_MAX = (
    df[
        (df["metric_key"].isin(["push_time", "rolling_time"]))
        & (df["trial_id"].isin(REPS))
    ]["value"].max() * 1.1
)

# =========================================================
# SECTION 1 — AVERAGE CYCLE SPEED
# =========================================================
st.subheader("Cycle Speed")
st.write(
    """
    This shows how fast you are moving during each cycle (push + rolling).Comparing the two phases (0-10m and 35-35m) highlights how you build your speed at the start
    and then once you've built up speed, mantain this over each cycle at the later stages of the sprint.
    """
)
col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = go.Figure()

        for rep in REPS:
            d = df[
                (df["trial_id"] == rep)
                & (df["distance_band"] == band)
                & (df["metric_key"] == "cycle_av_speed")
            ].sort_values("cycle_no")

            fig.add_scatter(
                x=d["cycle_no"],
                y=d["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=dict(color=REP_COLOURS[rep], width=2),
                marker=dict(size=6),
            )

        fig.update_layout(
            title=f"Average Cycle Speed ({band} m)",
            xaxis_title="Cycle",
            yaxis_title="Speed (m/s)",
            yaxis=dict(range=[0, GLOBAL_SPEED_MAX]),
            template="simple_white",
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 2 — CYCLE LENGTH BREAKDOWN
# =========================================================
# ======================================================
# CYCLE LENGTH DEFINITION POPOVER
# ======================================================

cycle_path = base_path / "images" / "cycle_definitions_image.png"
pushangle_path = base_path / "images" / "push_angle.png"

st.markdown("### Cycle Length Breakdown")

with st.popover("What is cycle length?"):
    st.markdown("#### 🔂 Cycle Length")

    st.write(
        """
        The distance travelled during each cycle.
        One **cycle** consists of:
            - the 👊***push phase*** (hands in contact with the push rim)
            - the🌀***rolling phase*** (hands off the rim while the chair freewheels)
        """
)
      

    if cycle_path.exists():
        st.image(
            str(cycle_path),
            caption="Push phase + rolling phase together make one cycle",
            use_container_width=True,
        )
    else:
        st.warning(f"Cycle definition image not found at: {cycle_path}")

    st.divider()

    st.markdown(
        """
        **Why cycle length matters**\n\n
        Cycle length reflects how effectively force application and rolling recovery are combined. 
        Changes can indicate technique adaptations/timing, fatigu or equipment efficiencies.
        """
        )  
# ======================================================
# CYCLE LENGTH Plot
# ======================================================

st.write(
    """
    The bars show how cycle length is made up of push distance and rolling distance. The line across the top of the bars shows total cycle length. 
    The rolling length is pretty consistent across the whole rep whilst your first pushes are the shortest this steadily increases, 
    and at 35-45m has reached a plateau, indicating like cycle speed a maintanence phase has been reached.
    """
)
col_left, col_right = st.columns(2)

for col, band in zip([col_left, col_right], DISTANCE_BANDS):
    with col:
        fig = go.Figure()

        df_len = df[
            (df["distance_band"] == band)
            & (df["metric_key"].isin(["push_length", "rolling_length"]))
            & (df["trial_id"].isin(REPS))
        ]

        cycles = sorted(df_len["cycle_no"].unique())

        for rep in REPS:
            r = df_len[df_len["trial_id"] == rep].sort_values("cycle_no")
            push = r[r["metric_key"] == "push_length"]
            roll = r[r["metric_key"] == "rolling_length"]

            x = push["cycle_no"].values + REP_OFFSET[rep]
            total = push["value"].values + roll["value"].values

            fig.add_bar(
                x=x, y=push["value"], width=0.32,
                marker_color=BAR_COLOURS["push_length"][rep],
                showlegend=False
            )

            fig.add_bar(
                x=x, y=roll["value"], base=push["value"], width=0.32,
                marker_color=BAR_COLOURS["rolling_length"][rep],
                showlegend=False
            )

            fig.add_scatter(
                x=x, y=total,
                mode="lines+markers",
                line=dict(color=REP_COLOURS[rep], width=2),
                marker=dict(size=7),
                showlegend=False,
            )

            fig.add_scatter(
                x=x, y=total + TEXT_PAD,
                mode="text",
                text=[f"{v:.2f}" for v in total],
                textfont=dict(size=TEXT_SIZE, color=REP_COLOURS[rep]),
                showlegend=False,
            )
            fig.update_layout(
                title=f"Cycle Length ({band} m)",
                barmode="stack",
                yaxis=dict(
                    range=[0, 3.2],                 # ✅ hard cap at 3.2
                    tickvals=[0, 1, 2, 3],           # ✅ labels only up to 3.0
                    ticktext=["0", "1", "2", "3"]
                ),
                xaxis=dict(
                    tickmode="array",
                    tickvals=cycles
                ),
                height=420,
                template="simple_white",
)



        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 3 — PUSH ANGLE
# =========================================================
# ======================================================
# PUSH ANGLE DEFINITION POPOVER
# ======================================================

st.markdown("### Push Angle Breakdown")

with st.popover("What is push angle?"):
    st.markdown("#### 👊 📐 Push Angle (degrees)")

    st.write(
        """       
        Total number of degrees you pushed the wheel through whilst your hands are in contact
        with the push rim. This does not describe where the push started or ended, only the
        total angular distance travelled by the hands on the rim.

        The push angle can be the same value for two very different push techniques, as shown
        by the shaded blue area below. In both cases the wheel was pushed through 105 degrees,
        but where the push occurred is different.
        """
    )

    if pushangle_path.exists():
        st.image(
            str(pushangle_path),
            use_container_width=True
        )
    else:
        st.warning(
            f"Push angle definition image not found at: {pushangle_path}"
        )

 
st.subheader("Push Angle")
st.write(
    """ Your first push has the smallest push angle, in your best rep this stabilised quickly over the first 5 pushes, 
    with a drop was seen in push 6, whereas for Rep 3 on push 4 you had a smaller push angle. When comparing your best rep and rep 
    3 over 35-45m it is interesting to note your push angle was decreasing for your best rep which is a possible indicator of fatigue.
    """
    )

col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = go.Figure()

        for rep in REPS:
            d = df[
                (df["trial_id"] == rep)
                & (df["distance_band"] == band)
                & (df["metric_key"] == "push_angle")
            ].sort_values("cycle_no")

            fig.add_scatter(
                x=d["cycle_no"],
                y=d["value"],
                mode="lines+markers",
                name=REP_LABELS[rep],
                line=dict(color=REP_COLOURS[rep], width=2),
                marker=dict(size=6),
            )

            fig.update_layout(
                title=f"Push Angle ({band} m)",
                xaxis_title="Cycle",
                yaxis_title="Angle (degrees)",
                yaxis=dict(range=[135, 225]),
                template="simple_white",
)


        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SECTION 4 — PUSH & ROLLING TIME
# =========================================================
st.subheader("Push and Rolling Time")
st.write(
    """
    "This shows how time is split between pushing and rolling in each cycle. 
    The Rolling time is constant acorss the entire sprint rep, whereas Push time is initially 
    high as you build momentum and get the chair rolling, then at 25m there is a transition where 
    Push time becomes shorter than Rolling time.
    """
)
col1, col2 = st.columns(2)

for col, band in zip([col1, col2], DISTANCE_BANDS):
    with col:
        fig = go.Figure()

        for rep in REPS:
            for metric in ["push_time", "rolling_time"]:
                d = df[
                    (df["trial_id"] == rep)
                    & (df["distance_band"] == band)
                    & (df["metric_key"] == metric)
                ].sort_values("cycle_no")

                fig.add_scatter(
                    x=d["cycle_no"],
                    y=d["value"],
                    mode="lines+markers",
                    name=f"{metric.replace('_', ' ').title()} – {REP_LABELS[rep]}",
                    line=dict(
                        color=REP_COLOURS[rep],
                        width=2.5 if metric == "rolling_time" else 2,
                        dash="dash" if metric == "rolling_time" else "solid",
                    ),
                    marker=dict(size=6),
                )

        fig.update_layout(
            title=f"Push & Rolling Time ({band} m)",
            xaxis_title="Cycle",
            yaxis_title="Time (s)",
            yaxis=dict(range=[0, GLOBAL_TIME_MAX]),
            template="simple_white",
        )

        st.plotly_chart(fig, use_container_width=True)
