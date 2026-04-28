# -*- coding: utf-8 -*-
"""
Torque vs Time Profile – Style‑aligned Plotly version
Author: Caroline Adams
"""

from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG 
# =========================================================
st.set_page_config(
    page_title="Lab testing Torque Profile",
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
# GLOBAL TEXT & UI STYLE (match other pages)
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        font-size: 18px;
        line-height: 1.55;
    }
    h1 { font-size: 40px; }
    h2 { font-size: 28px; margin-top: 1.2em; }
    h3 { font-size: 24px; margin-top: 1em; }
    .stCaption { font-size: 16px; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# PATHS
# =========================================================
ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
DATA = ROOT / "data"

# =========================================================
# HEADER
# =========================================================
logo = IMAGES / "Logo.png"
if logo.exists():
    st.image(str(logo), width=400)

st.title("Lab testing Torque Profile")

st.markdown(
    """
    This page shows the torque profiles that were measured in the lab using the instrumented ergometer. 
    From the two different 30 second push trials you did (baseline and higher resistance) the pushes were 
    analysed between 15-25 seconds once you had overcome the initial and were pushing consistently. The average torque 
    profile for each side is shown by the solid line, the faint shaded line represents the standard deviation (SD) 
    which is a metric to show how spread the data is from the average, were narrower bands show a greater consistency 
    between pushes. Angular impulse asymmetry describes how unevenly the total rotational effort is shared between 
    the left and right sides during each push. 
    
    Use the toggle to explore how your **symmetry and technique change under increased resistance.**
    """
)

# =========================================================
# PARAMETERS
# =========================================================
wheel_radius = 0.34
cutoff = 10.0
order = 4
push_threshold = 3.0
t0, t1 = 15, 25

# =========================================================
# SIGNAL PROCESSING FUNCTIONS
# =========================================================
def butter_lowpass(x, fs):
    b, a = butter(order, cutoff / (fs / 2), btype="low")
    return filtfilt(b, a, x)

def detect_pushes(time, torque, threshold):
    above = torque >= threshold
    edges = np.diff(above.astype(int))
    starts = np.where(edges == 1)[0] + 1
    ends = np.where(edges == -1)[0] + 1
    pushes = []
    e = 0
    for s in starts:
        while e < len(ends) and ends[e] <= s:
            e += 1
        if e >= len(ends):
            break
        pushes.append({"start": s, "end": ends[e], "t0": time[s]})
        e += 1
    return pushes

def extract_waves(df, pushes):
    waves = []
    for p in pushes:
        if t0 <= p["t0"] <= t1:
            s, e = p["start"], p["end"] + 1
            t = df["time"].values[s:e]
            y = df["torque"].values[s:e]
            if len(y) > 3:
                waves.append({"t": t - t[0], "y": y})
    return waves

def mean_sd(waves, n=200):
    if not waves:
        return None, None, None
    tmax = max(w["t"][-1] for w in waves)
    tc = np.linspace(0, tmax, n)
    Y = np.array([np.interp(tc, w["t"], w["y"]) for w in waves])
    return tc, Y.mean(axis=0), Y.std(axis=0)

def impulse(waves):
    if len(waves) < 2:
        return np.nan
    return np.mean(
        [np.trapezoid(w["y"], w["t"]) for w in waves]
    )

def asym(L, R):
    if np.isnan(L) or np.isnan(R):
        return np.nan
    return (L - R) / (0.5 * (L + R)) * 100

def angular_impulse(waves):
    """
    Mean angular impulse per push (area under torque–time curve).
    """
    if len(waves) < 2:
        return np.nan
    return np.mean(
        [np.trapezoid(w["y"], w["t"]) for w in waves]
    )

def angular_impulse_asymmetry(L, R):
    """
    Percentage angular impulse asymmetry.
    Positive = left side contributes more total work.
    """
    if np.isnan(L) or np.isnan(R):
        return np.nan
    return (L - R) / (0.5 * (L + R)) * 100

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_trial(file):
    L = pd.read_excel(file, sheet_name="Ergo_Left")
    R = pd.read_excel(file, sheet_name="Ergo_Right")
    for df in (L, R):
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
    fs = 1 / np.mean(np.diff(L["time"]))
    for df in (L, R):
        df["torque"] = butter_lowpass(df["force"], fs) * wheel_radius
    return (
        L, R,
        detect_pushes(L["time"], L["torque"], push_threshold),
        detect_pushes(R["time"], R["torque"], push_threshold),
    )

BL, BR, BLp, BRp = load_trial(DATA / "30Sec_baseline.xlsx")
RL, RR, RLp, RRp = load_trial(DATA / "30Sec_resisted.xlsx")

# =========================================================
# DISPLAY OPTIONS (matches other pages)
# =========================================================
st.markdown("### Display options")
show_resisted = st.toggle("Show resisted trial", value=False)

# =========================================================
# =========================================================
# DATA EXTRACTION
# =========================================================
BLw, BRw = extract_waves(BL, BLp), extract_waves(BR, BRp)
RLw, RRw = extract_waves(RL, RLp), extract_waves(RR, RRp)

# Mean angular impulse asymmetry (15–25 s window)
baseline_angular_impulse_asym = angular_impulse_asymmetry(
    angular_impulse(BLw),
    angular_impulse(BRw)
)

resisted_angular_impulse_asym = angular_impulse_asymmetry(
    angular_impulse(RLw),
    angular_impulse(RRw)
)

def mean_torque(waves):
    """
    True mean torque across real pushes (not time-normalised).
    """
    if len(waves) < 2:
        return np.nan
    return np.mean([
        np.mean(w["y"]) for w in waves
    ])

# Baseline
baseline_mean_torque_asym = angular_impulse_asymmetry(
    mean_torque(BLw),
    mean_torque(BRw)
)

# Resisted
resisted_mean_torque_asym = angular_impulse_asymmetry(
    mean_torque(RLw),
    mean_torque(RRw)
)
# =========================================================
# SECTION HEADER + ASYMMETRY
# =========================================================
col_l, col_r = st.columns([3, 2])

with col_l:
    st.subheader("Torque vs Time profile")

    with st.popover("What is torque?"):
        st.write(
            "🚀 Torque: represents the turning force applied to the wheel — a combined "
            "reflection of strength, technique, and timing."
        )

    with st.popover("What is angular impulse asymmetry?"):
        st.write(
            """
            Angular impulse asymmetry shows whether one arm contributes more
            **total work per push**.

            It reflects not just how hard you push, but **how long**
            and **when** force is applied during the push.
            """
        )

with col_r:
    st.markdown(
        f"""
        <div style="text-align:right; padding-top:8px;">
        <strong>Baseline angular impulse asymmetry:</strong>
        {baseline_angular_impulse_asym:+.1f}%<br>
        {"<strong>Resisted angular impulse asymmetry:</strong> "
         + f"{resisted_angular_impulse_asym:+.1f}%" if show_resisted else ""}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PLOT (STYLE‑MATCHED)
# =========================================================
fig = go.Figure()

def add_profile(t, m, sd, col, fill, name, dash=None):
    fig.add_scatter(
        x=t, y=m,
        mode="lines",
        line=dict(color=col, width=2.5, dash=dash),
        name=name
    )
    fig.add_scatter(
        x=np.r_[t, t[::-1]],
        y=np.r_[m - sd, (m + sd)[::-1]],
        fill="toself",
        fillcolor=fill,
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False
    )

t, m, sd = mean_sd(BLw); add_profile(t, m, sd, "red", "rgba(211,160,160,0.35)", "Baseline Left")
t, m, sd = mean_sd(BRw); add_profile(t, m, sd, "blue","rgba(158,197,255,0.35)", "Baseline Right")

if show_resisted:
    t, m, sd = mean_sd(RLw); add_profile(t, m, sd, "black","rgba(217,217,217,0.35)", "Resisted Left","dash")
    t, m, sd = mean_sd(RRw); add_profile(t, m, sd, "green","rgba(168,230,163,0.35)", "Resisted Right","dash")

fig.update_layout(
    template="simple_white",
    height=500,
    hovermode="x unified",
    legend=dict(font=dict(size=16)),
    xaxis=dict(title="Time from push start (s)", gridcolor="rgba(0,0,0,0.25)"),
    yaxis=dict(title="Torque (Nm)", gridcolor="rgba(0,0,0,0.25)")
)

plot_container_start(1150)
st.plotly_chart(fig, use_container_width=True)
plot_container_end()

# =========================================================
# INTERPRETATION
# =========================================================
st.markdown(
    """
    At baseline, propulsion shows **clear left‑dominance** and asymmetry. There is a clear difference in the shape of the 
    of the torque over time profile, with a higher peak torque for the left side and a shorter push time.
    Under resisted conditions, symmetry improves substantially, with peak torque and push time very similar suggesting
    modified technique and more balanced force application.
    """
)
# st.markdown("### 🔎 Asymmetry check (debug)")

# st.write("**Baseline:**")
# st.write(f"- Angular impulse asymmetry: {baseline_angular_impulse_asym:+.1f}%")
# st.write(f"- Mean torque asymmetry: {baseline_mean_torque_asym:+.1f}%")

# if show_resisted:
#     st.write("**Resisted:**")
#     st.write(f"- Angular impulse asymmetry: {resisted_angular_impulse_asym:+.1f}%")
#     st.write(f"- Mean torque asymmetry: {resisted_mean_torque_asym:+.1f}%")
    
# def debug_impulse(waves, label):
#     vals = [np.trapezoid(w["y"], w["t"]) for w in waves]
#     st.write(f"{label} pushes:", len(vals))
#     st.write(f"{label} impulse values:", np.round(vals, 2))
#     st.write(f"{label} mean impulse:", np.round(np.mean(vals), 2))

# st.write("### DEBUG IMPULSE VALUES")

# debug_impulse(BLw, "Baseline Left")
# debug_impulse(BRw, "Baseline Right")

# if show_resisted:
#     debug_impulse(RLw, "Resisted Left")
#     debug_impulse(RRw, "Resisted Right")