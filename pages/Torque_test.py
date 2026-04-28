# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:29:08 2026

@author: Caroline Adams
"""

# -*- coding: utf-8 -*-
"""
Torque Profile – Plotly Version (Style‑Matched)
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
st.set_page_config(layout="wide", page_title="Lab testing Torque Profile")

# =========================================================
# PATHS
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = PROJECT_ROOT / "images"
DATA_DIR = PROJECT_ROOT / "data"

# =========================================================
# HEADER
# =========================================================
logo_path = IMAGES_DIR / "Logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=400)

st.title("Lab testing Torque Profile")

st.markdown(
    """
    This view shows **mean ± SD torque–time profiles** for wheelchair propulsion.

    - Baseline condition is shown by default  
    - Toggle the resisted condition to explore how symmetry changes under load
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
# FUNCTIONS
# =========================================================
def butter_lowpass(x, fs):
    b, a = butter(order, cutoff / (fs / 2), btype="low")
    return filtfilt(b, a, x)

def detect_pushes(time, torque, threshold):
    above = torque >= threshold
    d = np.diff(above.astype(int))
    starts = np.where(d == 1)[0] + 1
    ends   = np.where(d == -1)[0] + 1
    pushes = []
    e_ptr = 0
    for s in starts:
        while e_ptr < len(ends) and ends[e_ptr] <= s:
            e_ptr += 1
        if e_ptr >= len(ends):
            break
        e = ends[e_ptr]
        pushes.append({"start": s, "end": e, "start_time": time[s]})
        e_ptr += 1
    return pushes

def extract_waves(df, pushes, t0, t1):
    waves = []
    for p in pushes:
        if t0 <= p["start_time"] <= t1:
            s, e = p["start"], p["end"] + 1
            t = df["time"].values[s:e]
            y = df["torque"].values[s:e]
            if len(y) >= 3:
                waves.append({"t": t - t[0], "y": y})
    return waves

def mean_sd_time(waves, n=200):
    if not waves:
        return None, None, None
    tmax = max(w["t"][-1] for w in waves)
    t_common = np.linspace(0, tmax, n)
    Y = np.array([np.interp(t_common, w["t"], w["y"]) for w in waves])
    return t_common, Y.mean(axis=0), Y.std(axis=0)

def impulse_stats(waves):
    if len(waves) < 2:
        return np.nan
    return np.trapz([np.trapz(w["y"], w["t"]) for w in waves])

def asymmetry_index(L, R):
    if np.isnan(L) or np.isnan(R) or (L + R) == 0:
        return np.nan
    return (L - R) / (0.5 * (L + R)) * 100

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_trial(fp):
    L = pd.read_excel(fp, sheet_name="Ergo_Left")
    R = pd.read_excel(fp, sheet_name="Ergo_Right")
    for df in (L, R):
        df["time"] = pd.to_numeric(df["time"], errors="coerce")
        df["force"] = pd.to_numeric(df["force"], errors="coerce")
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
    fs = 1 / np.mean(np.diff(L["time"]))
    for df in (L, R):
        df["force_filt"] = butter_lowpass(df["force"].values, fs)
        df["torque"] = df["force_filt"] * wheel_radius
    return (
        L, R,
        detect_pushes(L["time"], L["torque"], push_threshold),
        detect_pushes(R["time"], R["torque"], push_threshold)
    )

baseline_L, baseline_R, BLp, BRp = load_trial(DATA_DIR / "30Sec_baseline.xlsx")
resisted_L, resisted_R, RLp, RRp = load_trial(DATA_DIR / "30Sec_resisted.xlsx")

# =========================================================
# USER CONTROLS
# =========================================================
st.markdown("### Display options")
show_resisted = st.checkbox("Show resisted trial", value=False)

# =========================================================
# EXTRACT DATA
# =========================================================
BL = extract_waves(baseline_L, BLp, t0, t1)
BR = extract_waves(baseline_R, BRp, t0, t1)
RL = extract_waves(resisted_L, RLp, t0, t1)
RR = extract_waves(resisted_R, RRp, t0, t1)

baseline_asym = asymmetry_index(impulse_stats(BL), impulse_stats(BR))
resisted_asym = asymmetry_index(impulse_stats(RL), impulse_stats(RR))

# =========================================================
# ASYMMETRY HEADER
# =========================================================
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("## Torque vs Time profile")

with col2:
    st.markdown(
        f"""
        <div style="text-align:right; font-size:18px;">
        <strong>Baseline asymmetry:</strong> {baseline_asym:+.1f}%<br>
        {"<strong>Resisted asymmetry:</strong> " + f"{resisted_asym:+.1f}%" if show_resisted else ""}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PLOTLY FIGURE (STYLE‑MATCHED)
# =========================================================
fig = go.Figure()

def add_mean_sd(t, m, sd, line_col, fill_col, label, dash=None):
    fig.add_trace(go.Scatter(
        x=t, y=m,
        mode="lines",
        line=dict(color=line_col, width=2, dash=dash),
        name=label
    ))
    fig.add_trace(go.Scatter(
        x=np.concatenate([t, t[::-1]]),
        y=np.concatenate([m - sd, (m + sd)[::-1]]),
        fill="toself",
        fillcolor=fill_col,
        line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip",
        showlegend=False
    ))

t, m, sd = mean_sd_time(BL)
add_mean_sd(t, m, sd, "firebrick", "rgba(211,160,160,0.35)", "Baseline Left")

t, m, sd = mean_sd_time(BR)
add_mean_sd(t, m, sd, "royalblue", "rgba(158,197,255,0.35)", "Baseline Right")

if show_resisted:
    t, m, sd = mean_sd_time(RL)
    add_mean_sd(t, m, sd, "black", "rgba(217,217,217,0.35)", "Resisted Left", dash="dash")

    t, m, sd = mean_sd_time(RR)
    add_mean_sd(t, m, sd, "seagreen", "rgba(168,230,163,0.35)", "Resisted Right", dash="dash")

fig.update_layout(
    template="simple_white",
    height=480,
    hovermode="x unified",
    legend=dict(font=dict(size=14), frameon=False),
    xaxis=dict(
        title="Time from push start (s)",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.25)"
    ),
    yaxis=dict(
        title="Torque (Nm)",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.25)"
    )
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DISCUSSION
# =========================================================
st.markdown(
    """
    At normal resistance, you favour your **left side**, with ~25% asymmetry.
    Under increased load, your propulsion becomes more symmetrical —
    longer pushes and improved left–right balance (<1% asymmetry).
    """
)
