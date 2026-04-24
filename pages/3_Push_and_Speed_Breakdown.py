import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import math

# =========================================================
# PAGE SETUP
# =========================================================
st.title("Track Testing 60m reps")
st.write(
    "This page compares the four 60 m wheelchair racing sprints you did  "
    "looking at some key performance metrics and how they differ across 10 m splits."
)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_sprint_data():
    root = Path(__file__).resolve().parents[1]
    return pd.read_excel(
        root / "data" / "MW_60m_spatial_temporal.xlsx",
        sheet_name=0
    )

df = load_sprint_data()
trial_names = sorted(df["Trial"].dropna().unique())

# =========================================================
# FIXED COLOUR MAP (YOUR REQUEST)
# =========================================================
colour_map = {
    "60m_1": "#2ca02c",  # green
    "60m_2": "#2745C8",  # blue
    "60m_3": "#46A9D6",  # light blue
    "60m_4": "#9D32BE",  # purple
}

# =========================================================
# SECTION 1: ALL TRIALS OVERVIEW
# =========================================================
st.subheader("All trials overview")

for trial in trial_names:
    with st.expander(trial, expanded=False):
        tdf = df[df["Trial"] == trial]

        table = tdf.pivot(
            index="Metric",
            columns="Distance (m)",
            values="Value"
        )

        # remove 0–10 split
        table = table.loc[:, table.columns > 10]
        table.columns = [f"{int(c-10)}–{int(c)} m" for c in table.columns]

        st.dataframe(table.round(2), use_container_width=True)

# =========================================================
# SECTION 2: 60 m REP PROFILES
# =========================================================
st.subheader("60 m Rep profiles")

selected_trials = st.multiselect(
    "Select trials",
    trial_names,
    default=[trial_names[0]]
)

plot_metrics = [
    "Interval Time (s)",
    "Average Velocity (m/s)",
    "Average Cycle Length (m)",
    "Average Cycle Frequency (Hz)"
]

selected_metric = st.selectbox("Metric to plot", plot_metrics)

# -----------------------------
# VIEW MODES
# -----------------------------
show_minmax = st.toggle("Show min–max range across all reps")
compare_to_best = st.toggle("Compare to best rep")

# guardrail: only one mode visually active
if compare_to_best:
    show_minmax = False
    st.caption(
        "Compares one rep against your best. "
        "Only the best rep and the selected rep are shown, "
        "with arrows showing the difference at each split."
    )

if not selected_trials:
    st.warning("Please select at least one trial.")
    st.stop()

# =========================================================
# BEST REP (ALWAYS FROM ALL REPS)
# =========================================================
metric_all_df = df[df["Metric"] == selected_metric]
means = metric_all_df.groupby("Trial")["Value"].mean()

if selected_metric == "Interval Time (s)":
    best_trial = means.idxmin()
    best_desc = "lowest average interval time"
else:
    best_trial = means.idxmax()
    best_desc = "highest average value"

st.info(f"⭐ **Best rep:** {best_trial} ({best_desc})")

# =========================================================
# SELECT COMPARISON REP (COMPARE MODE)
# =========================================================
comparison_trial = None

if compare_to_best:
    non_best = [t for t in selected_trials if t != best_trial]
    if non_best:
        comparison_trial = non_best[-1]
    else:
        st.warning("Select a rep other than the best to compare.")
        compare_to_best = False

# =========================================================
# DISPLAY TRIALS
# =========================================================
if compare_to_best and comparison_trial:
    display_trials = [best_trial, comparison_trial]
else:
    display_trials = selected_trials

plot_df = df[
    (df["Trial"].isin(display_trials)) &
    (df["Metric"] == selected_metric)
]

# =========================================================
# MIN–MAX RANGE (ALWAYS ALL REPS)
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

# ---- MIN–MAX BAND (optional)
if show_minmax:
    fig.add_trace(
        go.Scatter(
            x=list(range_df["Distance (m)"]) +
              list(range_df["Distance (m)"][::-1]),
            y=list(range_df["max_val"]) +
              list(range_df["min_val"][::-1]),
            fill="toself",
            fillcolor="rgba(190,190,190,0.55)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Min–max range (all reps)",
            hoverinfo="skip"
        )
    )

# ---- LINES (FIXED LOOP)
for trial in display_trials:
    d = plot_df[plot_df["Trial"] == trial]
    is_best = (trial == best_trial)

    fig.add_trace(
        go.Scatter(
            x=d["Distance (m)"],
            y=d["Value"],
            mode="lines+markers",
            name="★ Best rep" if is_best else trial,
            marker=dict(
                symbol="diamond",
                size=8,
                color=colour_map[trial]
            ),
            line=dict(
                width=2,
                color=colour_map[trial]
            ),
            opacity=1.0 if is_best else 0.7
        )
    )

# =========================================================
# COMPARE‑TO‑BEST: ARROWS + NUMERIC CALLOUTS ONLY
# =========================================================
if compare_to_best and comparison_trial:
    best_df = plot_df[plot_df["Trial"] == best_trial]
    comp_df = plot_df[plot_df["Trial"] == comparison_trial]

    for _, row in comp_df.iterrows():
        best_val = best_df.loc[
            best_df["Distance (m)"] == row["Distance (m)"],
            "Value"
        ].values[0]

        delta = row["Value"] - best_val

        # direction logic
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
    xaxis=dict(
        title="Distance (m)",
        range=[-2, 65],
        dtick=10
    ),
    yaxis=dict(
        title=selected_metric,
        range=[-0.25, y_upper],
        tick0=0,
        dtick=0.5
    ),
    hovermode="x unified",
    legend_title="Legend"
)


st.markdown(
    "<p style='color: black; font-size: 14px;'>"
    "<strong>Chart navigation:</strong> "
    "Click and drag to draw a box to zoom in on areas of interest, "
    "then double‑click to zoom back out."
    "</p>",
    unsafe_allow_html=True
)

st.plotly_chart(fig, use_container_width=True)

