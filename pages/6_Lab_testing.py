# -*- coding: utf-8 -*-# Caroline Adams

# ======================================================
# IMPORTS
# ======================================================
from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

# ======================================================
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# ======================================================
st.set_page_config(
    page_title="Lab Testing - Torque Profile",
    layout="wide"
)

st.markdown(
    """
    This view shows **mean ± SD torque–time profiles** for wheelchair propulsion.
    
    - Baseline condition is shown by default  
    - Toggle the resisted condition to see how symmetry changes under load  
    """
)

# ======================================================
# PAGE SETUP
# ======================================================
logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=400)

# ======================================================
# PARAMETERS
# ======================================================
wheel_radius = 0.34
cutoff = 10.0
order = 4
push_threshold = 3.0
t0, t1 = 15, 25

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
    tc = np.linspace(0, tmax, n)
    Y = np.array([np.interp(tc, w["t"], w["y"]) for w in waves])
    return tc, Y.mean(axis=0), Y.std(axis=0)


def compute_push_impulse(wave):
    return np.trapezoid(wave["y"], wave["t"])


def impulse_stats(waves):
    if len(waves) < 2:
        return np.nan, np.nan
    impulses = [compute_push_impulse(w) for w in waves]
    return np.mean(impulses), np.std(impulses, ddof=1)


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
# BUILD TORQUE COMPARISON PLOT
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

fig, ax = plt.subplots(figsize=(10, 5))

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
        ax.plot(t, m, color="black", linestyle="--", linewidth=2, label="Resisted Left")
        ax.fill_between(t, m - sd, m + sd, color="#d9d9d9", alpha=0.35)

    t, m, sd = mean_sd_time(RR_T)
    if t is not None:
        ax.plot(t, m, color="green", linestyle="--", linewidth=2, label="Resisted Right")
        ax.fill_between(t, m - sd, m + sd, color="#a8e6a3", alpha=0.35)

# Annotation
text = f"Baseline asymmetry: {baseline_asym:+.1f}%"
if show_resisted:
    text += f"\nResisted asymmetry: {resisted_asym:+.1f}%"

ax.text(
    0.02, 0.95,
    text,
    transform=ax.transAxes,
    va="top",
    fontsize=10,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
)

ax.set_title("Torque vs Time (15–25 s)")
ax.set_xlabel("Time from push start (s)")
ax.set_ylabel("Torque (Nm)")
ax.legend()
ax.grid(alpha=0.3)

st.pyplot(fig)

