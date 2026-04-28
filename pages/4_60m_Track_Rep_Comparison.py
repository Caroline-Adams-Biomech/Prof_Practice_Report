import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import math

# =========================================================
# PAGE CONFIG — MUST BE FIRST
# =========================================================
st.set_page_config(
    page_title="Track Testing 60m reps",
    layout="wide"
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

# =========================================================
# METRIC TEXT
# =========================================================
st.title("Track Testing 60m reps")

st.write(
    "This page compares the four 60m sprint repetitions you completed, "
    "focusing on key performance metrics across 10 m splits."
)

# =========================================================
# METRIC DEFINITIONS — SINGLE COLUMN
# =========================================================
st.write("### Key Metrics")

with st.popover("⏱️ Interval Time (s)"):
    st.subheader("⏱️ Interval Time (seconds)")
    st.write(
        "Time taken to travel from the start to the end of each segment "
        "(e.g. 0–10 m, 10–20 m)."
    )

with st.popover("💨 Average Speed (m/s)"):
    st.subheader("💨 Average Speed (m/s)")
    st.write(
        "The average speed of the athlete and chair during each 10 m split."
    )

with st.popover("🔂📏 Average Cycle Length (m)"):
    st.subheader("🔂📏 Average Cycle Length (m)")
    st.markdown(
        """
        The average distance travelled during each 10 m split.

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
    st.write(
        "The average number of cycles completed per second (CPS) during each "
        "10 m split — an indicator of cadence or arm speed."
    )

st.write(
    "We are mostly interested in the **shape of the curves**, as these reflect "
    "your individual push signature. Exact values are provided in the tables below."
)

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
# METRIC MAP (UI LABEL → DATA KEY)
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

st.write(
    "Select a **metric of interest** and the trials you would like to view. "
    "You can also compare a single repetition against your **best rep** to "
    "explore differences across each 10 m split."
)

st.caption("ℹ️ Best rep is recalculated separately for each metric.")

st.divider()

# -----------------------------
# METRIC SELECTION
# -----------------------------
st.markdown("#### Metric selection")

selected_metric = st.selectbox(
    "Metric to plot",
    list(METRIC_MAP.keys())
)

metric_key = METRIC_MAP[selected_metric]
metric_all_df = df[df["Metric"] == metric_key]

if metric_all_df.empty:
    st.error(f"No data found for metric '{selected_metric}'.")
    st.stop()

# --- Determine best rep for this metric
means = metric_all_df.groupby("Trial")["Value"].mean()

if selected_metric == "Interval Time (s)":
    best_trial = means.idxmin()
    best_desc = "lowest average interval time"
else:
    best_trial = means.idxmax()
    best_desc = "highest average value"

st.info(f"⭐ **Best rep:** {best_trial} ({best_desc})")

st.divider()

# -----------------------------
# TRIAL SELECTION
# -----------------------------
st.markdown("#### Trials of interest")

# Compare toggle + info popover inline
col_toggle, col_info = st.columns([1, 0.05])

with col_toggle:
    compare_to_best = st.toggle("Compare one rep to your best rep")

with col_info:
    with st.popover("ℹ️"):
        st.markdown(
            """
            **Compare to best rep**

            This mode allows you to select **one repetition** and compare it
            directly against your **best rep** for the selected metric.

            Differences at each 10 m split are shown using arrows and values.
            """
        )

# --- Disable trial multiselect when in compare mode
selected_trials = st.multiselect(
    "Trials of interest",
    trial_names,
    default=trial_names[:1],
    disabled=compare_to_best
)

# Visually signal why selection is disabled
if compare_to_best:
    st.caption(
        "Trial selection is disabled while comparing to best rep."
    )

if not compare_to_best and not selected_trials:
    st.warning("Please select at least one trial.")
    st.stop()

st.divider()

# -----------------------------
# DISPLAY MODE LOGIC
# -----------------------------
if compare_to_best:
    comparison_trial = st.selectbox(
        "Select a rep to compare against your best",
        [t for t in trial_names if t != best_trial]
    )

    display_trials = [best_trial, comparison_trial]
    show_minmax = False  # disabled in compare mode

    st.caption(
        f"🔍 Now comparing **{comparison_trial}** against "
        f"**{best_trial} (best rep)** across each 10 m split."
    )

else:
    display_trials = selected_trials

    show_minmax = st.toggle(
        "Show min–max range across all reps",
        value=False
    )

# ---------------------------------------------------------
# MODE TOGGLE
# ---------------------------------------------------------
compare_to_best = st.toggle("Compare a rep to your best rep")

if compare_to_best:
    # ---------- COMPARE MODE ----------
    comparison_trial = st.selectbox(
        "Select a rep to compare against your best",
        [t for t in trial_names if t != best_trial]
    )

    display_trials = [best_trial, comparison_trial]
    show_minmax = False  # disabled in compare mode

    st.info(
        f"🔍 Comparing **{comparison_trial}** against "
        f"**{best_trial} (best rep)**"
    )

else:
    # ---------- NORMAL MODE ----------
    selected_trials = st.multiselect(
        "Select trials",
        trial_names,
        default=trial_names[:1]
    )

    if not selected_trials:
        st.warning("Please select at least one trial.")
        st.stop()

    display_trials = selected_trials
    show_minmax = st.toggle("Show min–max range across all reps")
# # =========================================================
# # SECTION: REP PROFILES
# # =========================================================
# st.subheader("60 m Rep profiles")

# selected_trials = st.multiselect(
#     "Select trials",
#     trial_names,
#     default=trial_names[:1]
# )

# selected_metric = st.selectbox(
#     "Metric to plot",
#     list(METRIC_MAP.keys())
# )

# show_minmax = st.toggle("Show min–max range across all reps")
# compare_to_best = st.toggle("Compare a rep to your best rep")

# if compare_to_best:
#     show_minmax = False
#     st.caption(
#         "Compares one rep against your best rep. "
#         "Only two lines are shown with arrows indicating differences."
#     )

# if not selected_trials:
#     st.warning("Please select at least one trial.")
#     st.stop()



# =========================================================
# BEST REP
# =========================================================
means = metric_all_df.groupby("Trial")["Value"].mean()

if selected_metric == "Interval Time (s)":
    best_trial = means.idxmin()
    best_desc = "lowest average interval time"
else:
    best_trial = means.idxmax()
    best_desc = "highest average value"

st.info(f"⭐ **Best rep:** {best_trial} ({best_desc})")

# =========================================================
# DISPLAY TRIALS
# =========================================================

if compare_to_best:
    # Compare mode: always exactly two known trials
    display_trials = [best_trial, comparison_trial]

else:
    # Normal mode: user-selected trials
    display_trials = selected_trials

plot_df = df[
    (df["Trial"].isin(display_trials)) &
    (df["Metric"] == metric_key)
]

# =========================================================
# MIN–MAX RANGE (ALL REPS)
# =========================================================
range_df = (
    metric_all_df
    .groupby("Distance (m)")
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
            fillcolor="rgba(180,180,180,0.4)",
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            name="Min–max range (all reps)"
        )
    )

for trial in display_trials:
    d = plot_df[plot_df["Trial"] == trial]
    fig.add_trace(
        go.Scatter(
            x=d["Distance (m)"],
            y=d["Value"],
            mode="lines+markers",
            name=("★ Best rep" if trial == best_trial else trial),
            line=dict(color=colour_map[trial], width=2),
            marker=dict(size=7),
        )
    )

# =========================================================
# COMPARE‑TO‑BEST ANNOTATIONS
# =========================================================
if compare_to_best and comparison_trial:
    best_df = plot_df[plot_df["Trial"] == best_trial]
    comp_df = plot_df[plot_df["Trial"] == comparison_trial]

    for _, row in comp_df.iterrows():
        best_val = best_df.loc[
            best_df["Distance (m)"] == row["Distance (m)"], "Value"
        ].values[0]

        delta = row["Value"] - best_val

        if selected_metric == "Interval Time (s)":
            worse = row["Value"] > best_val
        else:
            worse = row["Value"] < best_val

        colour = "rgb(200,60,60)" if worse else "rgb(120,120,120)"

        fig.add_annotation(
            x=row["Distance (m)"],
            y=row["Value"],
            text=f"{delta:+.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=colour,
            font=dict(color=colour, size=11),
            ay=-30
        )

# =========================================================
# AXES & LAYOUT
# =========================================================
raw_y_max = metric_all_df["Value"].max()
y_upper = math.ceil((raw_y_max + 0.5) * 2) / 2

fig.update_layout(
    height=450,
    xaxis=dict(title="Distance (m)", range=[-2, 65], dtick=10),
    yaxis=dict(title=selected_metric, range=[-0.25, y_upper], dtick=0.5),
    hovermode="x unified",
    legend_title="Legend"
)

# =========================================================
# ZOOM / RESET INSTRUCTIONS
# =========================================================
st.markdown(
    "<p style='font-size:14px;'>"
    "<strong>Chart navigation:</strong> "
    "Click and drag to draw a box to zoom in, "
    "then double‑click anywhere on the plot to reset."
    "</p>",
    unsafe_allow_html=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# OVERVIEW TABLES
# =========================================================
st.subheader("All trials overview")

for trial in trial_names:
    with st.expander(trial):
        tdf = df[df["Trial"] == trial]
        table = tdf.pivot(
            index="Metric",
            columns="Distance (m)",
            values="Value"
        )

        table = table.loc[:, table.columns > 10]
        table.columns = [f"{int(c-10)}–{int(c)} m" for c in table.columns]

        st.dataframe(table.round(2), use_container_width=True)