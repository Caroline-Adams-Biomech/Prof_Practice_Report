# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 13:18:49 2026

@author: Caroline Adams
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 13:03:41 2026

@author: Caroline Adams
"""
# ======================================================
# BASELINE + RESISTED wheelchair ergometer analysis
# Mean ± SD Torque & Power
# Push-normalised time and % push cycle
# Impulse & asymmetry
# ======================================================
# -*- coding: utf-8 -*-# -*- coding: plot (Baseline vs Resisted, 15–25 s)


# ======================================================
# IMPORTS (EXPLICIT)
# ======================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# ======================================================
# PARAMETERS (SHARED)
# ======================================================
wheel_radius = 0.34
cutoff = 10.0
order = 4
push_threshold = 3.0

cases = [
    ("All pushes", 0, np.inf),
    ("5–30 s", 5, 30),
    ("10–30 s", 10, 30),
    ("15–25 s", 15, 25),
]

# ======================================================
# FILTER
# ======================================================
def butter_lowpass(x, fs):
    b, a = butter(order, cutoff / (fs / 2), btype="low")
    return filtfilt(b, a, x)

# ======================================================
# PUSH DETECTION (ROBUST, SAME FOR BOTH)
# ======================================================
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

# ======================================================
# PUSH WAVE EXTRACTION
# ======================================================
def extract_waves(df, pushes, t0, t1, signal):
    waves = []
    for p in pushes:
        if t0 <= p["start_time"] <= t1:
            s = p["start"]
            e = p["end"] + 1
            t = df["time"].values[s:e]
            y = df[signal].values[s:e]
            if len(y) >= 3:
                waves.append({"t": t - t[0], "y": y})
    return waves

# ======================================================
# MEAN ± SD (TIME)
# ======================================================
def mean_sd_time(waves, n=200):
    if not waves:
        return None, None, None
    tmax = max(w["t"][-1] for w in waves)
    tc = np.linspace(0, tmax, n)
    Y = np.array([np.interp(tc, w["t"], w["y"]) for w in waves])
    return tc, Y.mean(axis=0), Y.std(axis=0)

# ======================================================
# MEAN ± SD (% PUSH)
# ======================================================
def mean_sd_percent(waves, n=200):
    if not waves:
        return None, None, None
    pc = np.linspace(0, 100, n)
    Y = []
    for w in waves:
        x = np.linspace(0, 100, len(w["y"]))
        Y.append(np.interp(pc, x, w["y"]))
    Y = np.array(Y)
    return pc, Y.mean(axis=0), Y.std(axis=0)

# ======================================================
# IMPULSE & ASYMMETRY (TORQUE)
# ======================================================
def compute_push_impulse(wave):
    return np.trapezoid(wave["y"], wave["t"])

def impulse_stats(waves):
    if len(waves) < 2:
        return np.nan, np.nan
    imp = [compute_push_impulse(w) for w in waves]
    return np.mean(imp), np.std(imp, ddof=1)

def asymmetry_index(L, R):
    if np.isnan(L) or np.isnan(R) or (L + R) == 0:
        return np.nan
    return (L - R) / (0.5 * (L + R)) * 100

# ======================================================
# LOAD & PROCESS A TRIAL
# ======================================================
def load_trial(filename, has_speed=False):
    L = pd.read_excel(filename, sheet_name="Ergo_Left")
    R = pd.read_excel(filename, sheet_name="Ergo_Right")

    for df in (L, R):
        df["time"]  = pd.to_numeric(df["time"], errors="coerce")
        df["force"] = pd.to_numeric(df["force"], errors="coerce")
        if has_speed:
            df["speed"] = pd.to_numeric(df["speed"], errors="coerce")
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

    fs = 1 / np.mean(np.diff(L["time"].values))

    for df in (L, R):
        df["force_filt"] = butter_lowpass(df["force"].values, fs)
        df["torque"] = df["force_filt"] * wheel_radius
        if has_speed:
            df["speed_filt"] = butter_lowpass(df["speed"].values, fs)
            df["omega"] = df["speed_filt"] / wheel_radius
            df["power"] = df["torque"] * df["omega"]

    L_pushes = detect_pushes(L["time"].values, L["torque"].values, push_threshold)
    R_pushes = detect_pushes(R["time"].values, R["torque"].values, push_threshold)

    return L, R, L_pushes, R_pushes

# ======================================================
# LOAD BOTH TRIALS
# ======================================================
baseline_L, baseline_R, BLp, BRp = load_trial("30Sec_baseline.xlsx", has_speed=False)
resisted_L, resisted_R, RLp, RRp = load_trial("30Sec_resisted.xlsx", has_speed=True)

def compute_push_impulse(wave):
    """Torque impulse (Nm·s) for a single push"""
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

# ======================================================#15–25 s)
# Mean ± SD + Impulse Asymmetry
# ======================================================
t0, t1 = 15, 25

BL_T = extract_waves(baseline_L, BLp, t0, t1, "torque")
BR_T = extract_waves(baseline_R, BRp, t0, t1, "torque")

RL_T = extract_waves(resisted_L, RLp, t0, t1, "torque")
RR_T = extract_waves(resisted_R, RRp, t0, t1, "torque")

# ---- Impulse & asymmetry (baseline and resisted) ----
BL_imp, _ = impulse_stats(BL_T)
BR_imp, _ = impulse_stats(BR_T)
baseline_asym = asymmetry_index(BL_imp, BR_imp)

RL_imp, _ = impulse_stats(RL_T)
RR_imp, _ = impulse_stats(RR_T)
resisted_asym = asymmetry_index(RL_imp, RR_imp)

plt.figure(figsize=(10, 5))

# ------------------------------------------------------
# BASELINE — LEFT (solid red, grey-red SD)
# ------------------------------------------------------
t, m, sd = mean_sd_time(BL_T)
if t is not None:
    plt.plot(t, m, color="red", linewidth=2, label="Baseline Left")
    plt.fill_between(t, m - sd, m + sd, color="#d3a0a0", alpha=0.35)

# ------------------------------------------------------
# BASELINE — RIGHT (solid blue, blue SD)
# ------------------------------------------------------
t, m, sd = mean_sd_time(BR_T)
if t is not None:
    plt.plot(t, m, color="blue", linewidth=2, label="Baseline Right")
    plt.fill_between(t, m - sd, m + sd, color="#9ec5ff", alpha=0.35)

# ------------------------------------------------------
# RESISTED — LEFT (dashed black, light grey SD)
# ------------------------------------------------------
t, m, sd = mean_sd_time(RL_T)
if t is not None:
    plt.plot(t, m, color="black", linestyle="--", linewidth=2, label="Resisted Left")
    plt.fill_between(t, m - sd, m + sd, color="#d9d9d9", alpha=0.35)

# ------------------------------------------------------
# RESISTED — RIGHT (dashed green, light green SD)
# ------------------------------------------------------
t, m, sd = mean_sd_time(RR_T)
if t is not None:
    plt.plot(t, m, color="green", linestyle="--", linewidth=2, label="Resisted Right")
    plt.fill_between(t, m - sd, m + sd, color="#a8e6a3", alpha=0.35)

# ------------------------------------------------------
# Asymmetry annotation
# ------------------------------------------------------
asym_text = (
    f"Baseline asymmetry: {baseline_asym:+.1f}%\n"
    f"Resisted asymmetry: {resisted_asym:+.1f}%"
)

plt.text(
    0.02, 0.95,
    asym_text,
    transform=plt.gca().transAxes,
    va="top",
    fontsize=10,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
)

# ------------------------------------------------------
# FINAL FORMATTING
# ------------------------------------------------------
plt.title("Torque vs Time (15–25 s)")
plt.xlabel("Time from push start (s)")
plt.ylabel("Torque (Nm)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()



