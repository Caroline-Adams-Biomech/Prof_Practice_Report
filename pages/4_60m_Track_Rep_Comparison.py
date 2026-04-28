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
        "Time taken to travel from the start to the end of each segment, "
        "effectively a split time (e.g. 0–10 m, 10–20 m, etc.)."
    )

with st.popover("💨 Average Speed (m/s)"):
    st.subheader("💨 Average Speed (m/s)")
    st.write("The average speed of the athlete and chair during each 10 m split.")

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
        "10 m split — essentially an arm speed or cadence measure."
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
# METRIC MAP  ✅ THIS FIXES YOUR ERROR
# =========================================================
METRIC_MAP = {
    "Interval Time (s)": "Interval Time (s)",
    "Average Speed (m/s)": "Average Velocity (m/s)",
    "Average Cycle Length (m)": "Average Cycle Length (m)",
    "Average Cycle Frequency (CPS)": "Average Cycle Frequency (Hz)",
}

# =========================================================
# FIXED COLOUR MAP
# =========================================================
colour_map = {
    "60m_1": "#2ca02c",
    "60m_2": "#2745C8",
    "60m_3": "#46A9D6",
    "60m_4": "#9D32BE",
}

# =========================================================
# SECTION 2: REP PROFILES
# =========================================================
st.subheader("60 m Rep profiles")

selected_trials = st.multiselect(
    "Select trials",
    trial_names,
    default=trial_names[:1]
)

selected_metric = st.selectbox(
    "Metric to plot",
    list(METRIC_MAP.keys())
)

show_minmax = st.toggle("Show min–max range across all reps")
compare_to_best = st.toggle("Compare to best rep")

if not selected_trials:
    st.warning("Please select at least one trial.")
    st.stop()

# =========================================================
# DATA FILTERING (USING METRIC MAP)
# =========================================================
metric_key = METRIC_MAP[selected_metric]
metric_all_df = df[df["Metric"] == metric_key]

if metric_all_df.empty:
    st.error(f"No data found for metric '{selected_metric}'.")
    st.stop()

# =========================================================
# BEST REP
# =========================================================
means = metric_all_df.groupby("Trial")["Value"].mean()

if selected_metric == "Interval Time (s)":
    best_trial = means.idxmin()
else:
    best_trial = means.idxmax()

# =========================================================
# DISPLAY TRIALS
# =========================================================
display_trials = selected_trials
plot_df = df[
    (df["Trial"].isin(display_trials)) &
    (df["Metric"] == metric_key)
]

# =========================================================
# PLOT
# =========================================================
fig = go.Figure()

for trial in display_trials:
    d = plot_df[plot_df["Trial"] == trial]
    fig.add_trace(
        go.Scatter(
            x=d["Distance (m)"],
            y=d["Value"],
            mode="lines+markers",
            name=trial,
            line=dict(color=colour_map[trial], width=2),
            marker=dict(size=7),
        )
    )

fig.update_layout(
    height=450,
    xaxis=dict(title="Distance (m)", dtick=10),
    yaxis=dict(title=selected_metric),
    hovermode="x unified",
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