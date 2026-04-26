# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 15:23:59 2026

@author: Caroline Adams
"""
# =========================================================
# PAGE SETUP
# =========================================================
from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# =========================================================
# Helper: robust image loader (png / jpg / jpeg)
# =========================================================
def load_image(image_dir: Path, stem: str):
    """
    Attempt to load an image using common extensions.
    Returns the Path if found, otherwise None.
    """
    for ext in [".png", ".jpg", ".jpeg"]:
        candidate = image_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None

# =========================================================
# Base paths (multipage-safe)
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = PROJECT_ROOT / "images"

# =========================================================
# Load images safely
# =========================================================
logo_path = load_image(IMAGES_DIR, "Logo")

# =========================================================
# Header / Logo
# =========================================================
if logo_path:
    st.image(str(logo_path), width=400)
else:
    st.error(
        "Logo image not found. Expected one of:\n"
        "Logo.png / Logo.jpg / Logo.jpeg\n"
        f"in {IMAGES_DIR}"
    )

st.title("Lab testing Torque Profile")
st.markdown(
    """
    This view shows **mean ± SD torque–time profiles** for wheelchair propulsion.
    
    - Baseline condition is shown by default  
    - Toggle the resisted condition to see how symmetry changes under load  
    """
)

# ======================================================
# PARAMETERS
# ======================================================
wheel_radius = 0.34
cutoff = 10.0
order = 4
push_threshold = 3.0
t0, t1 = 15, 25  # analysis window (s)

# ======================================================
# FUNCTIONS
# ======================================================
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
            s = p["start"]
            e = p["end"] + 1
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

def compute_push_impulse(wave):
    return np.trapezoid(wave["y"], wave["t"])

def impulse_stats(waves):
    if len(waves) < 2:
        return np.nan, np.nan
    vals = [compute_push_impulse(w) for w in waves]
    return np.mean(vals), np.std(vals, ddof=1)

def asymmetry_index(L, R):
    if np.isnan(L) or np.isnan(R) or (L + R) == 0:
        return np.nan
    return (L - R) / (0.5 * (L + R)) * 100

# ======================================================
# LOAD & PROCESS DATA (CACHED)
# ======================================================
@st.cache_data
def load_trial(filepath):
    L = pd.read_excel(filepath, sheet_name="Ergo_Left")
    R = pd.read_excel(filepath, sheet_name="Ergo_Right")

    for df in (L, R):
        df["time"]  = pd.to_numeric(df["time"], errors="coerce")
        df["force"] = pd.to_numeric(df["force"], errors="coerce")
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

    fs = 1 / np.mean(np.diff(L["time"].values))

    for df in (L, R):
        df["force_filt"] = butter_lowpass(df["force"].values, fs)
        df["torque"] = df["force_filt"] * wheel_radius

    L_pushes = detect_pushes(L["time"].values, L["torque"].values, push_threshold)
    R_pushes = detect_pushes(R["time"].values, R["torque"].values, push_threshold)

    return L, R, L_pushes, R_pushes

data_path = Path(__file__).resolve().parents[1] / "data"

baseline_L, baseline_R, BLp, BRp = load_trial(data_path / "30Sec_baseline.xlsx")
resisted_L, resisted_R, RLp, RRp = load_trial(data_path / "30Sec_resisted.xlsx")

# ======================================================
# USER CONTROLS
# ======================================================
st.markdown("### Display options")
show_resisted = st.checkbox("Show resisted trial", value=False)

# ======================================================
# DATA EXTRACTION
# ======================================================
BL_T = extract_waves(baseline_L, BLp, t0, t1)
BR_T = extract_waves(baseline_R, BRp, t0, t1)
RL_T = extract_waves(resisted_L, RLp, t0, t1)
RR_T = extract_waves(resisted_R, RRp, t0, t1)

BL_imp, _ = impulse_stats(BL_T)
BR_imp, _ = impulse_stats(BR_T)
baseline_asym = asymmetry_index(BL_imp, BR_imp)

RL_imp, _ = impulse_stats(RL_T)
RR_imp, _ = impulse_stats(RR_T)
resisted_asym = asymmetry_index(RL_imp, RR_imp)

# ======================================================
# TITLE + ASYMMETRY HEADER (STREAMLIT LAYOUT)
# ======================================================
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(
        "Torque vs Time profile",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="
            text-align:right;
            font-size:18px;
            line-height:1.5;
            padding-top:8px;">
            <strong>Baseline asymmetry:</strong> {baseline_asym:+.1f}%<br>
            {"<strong>Resisted asymmetry:</strong> " + f"{resisted_asym:+.1f}%" if show_resisted else ""}
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# PLOT (CLEAN, DASHBOARD STYLE)
# ======================================================
fig, ax = plt.subplots(figsize=(11, 5))

# Axis styling
ax.tick_params(axis="both", labelsize=13)
ax.set_xlabel("Time from push start (s)", fontsize=14)
ax.set_ylabel("Torque (Nm)", fontsize=14)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, alpha=0.25)

# Baseline
t, m, sd = mean_sd_time(BL_T)
if t is not None:
    ax.plot(t, m, color="red", linewidth=2, label="Baseline Left")
    ax.fill_between(t, m - sd, m + sd, color="#d3a0a0", alpha=0.35)

t, m, sd = mean_sd_time(BR_T)
if t is not None:
    ax.plot(t, m, color="blue", linewidth=2, label="Baseline Right")
    ax.fill_between(t, m - sd, m + sd, color="#9ec5ff", alpha=0.35)

# Resisted (optional)
if show_resisted:
    t, m, sd = mean_sd_time(RL_T)
    if t is not None:
        ax.plot(t, m, color="black", linestyle="--",
                linewidth=2, label="Resisted Left")
        ax.fill_between(t, m - sd, m + sd, color="#d9d9d9", alpha=0.35)

    t, m, sd = mean_sd_time(RR_T)
    if t is not None:
        ax.plot(t, m, color="green", linestyle="--",
                linewidth=2, label="Resisted Right")
        ax.fill_between(t, m - sd, m + sd, color="#a8e6a3", alpha=0.35)

ax.legend(fontsize=12, frameon=False, loc="upper right")

st.pyplot(fig)

#Discussion
st.markdown(
    """
    At normal resistance you favour your left side is more dominant, we can see an assymetry between 
    your left and right side with a 25% difference between sides.When the load goes up, your technique
    actually gets more symmetrical — longer pushes, and balance between arms <1% assymetry.
    """
)