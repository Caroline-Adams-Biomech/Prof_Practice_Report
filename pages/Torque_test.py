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
# PAGE CONFIG (must be first)
# =========================================================
st.set_page_config(
    page_title="Lab testing Torque Profile",
    layout="wide"
)

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
    This view shows **mean ± SD torque–time profiles** for wheelchair propulsion.

    Use the toggle to explore how **symmetry and technique change under load**.
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
    return np.mean([np.trapz(w["y"], w["t"]) for w in waves])

def asym(L, R):
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
show_resisted = st.toggle("Show resisted trial", value=True)

# =========================================================
# DATA EXTRACTION
# =========================================================
BLw, BRw = extract_waves(BL, BLp), extract_waves(BR, BRp)
RLw, RRw = extract_waves(RL, RLp), extract_waves(RR, RRp)

base_asym = asym(impulse(BLw), impulse(BRw))
res_asym = asym(impulse(RLw), impulse(RRw))

# =========================================================
# SECTION HEADER + ASYMMETRY
# =========================================================
col_l, col_r = st.columns([3, 2])
with col_l:
    st.subheader("Torque vs Time profile")
    with st.popover("What is torque?"):
        st.write(
            "Torque represents the turning force applied to the wheel — a combined "
            "reflection of strength, technique, and timing."
        )

with col_r:
    st.markdown(
        f"""
        <div style="text-align:right; padding-top:8px;">
        <strong>Baseline asymmetry:</strong> {base_asym:+.1f}%<br>
        {"<strong>Resisted asymmetry:</strong> " + f"{res_asym:+.1f}%" if show_resisted else ""}
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

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# INTERPRETATION
# =========================================================
st.markdown(
    """
    At baseline, propulsion shows **clear left‑dominance** and asymmetry.
    Under resisted conditions, symmetry improves substantially, suggesting
    modified technique and more balanced force application.
    """
)
