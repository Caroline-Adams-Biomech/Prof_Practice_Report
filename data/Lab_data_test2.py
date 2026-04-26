# -*- coding: utf-8 -*-
"""
Mean ± SD torque profiles (LEFT vs RIGHT)
Multiple time windows, 3 Nm relaxed torque threshold
Includes push impulse annotation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# ======================================================
# PARAMETERS
# ======================================================
wheel_radius = 0.34
cutoff = 10.0
order = 4
push_threshold = 3.0  # Nm

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
# PUSH DETECTION (RELAXED TORQUE THRESHOLD)
# ======================================================
def detect_pushes(time, torque, threshold):
    above = torque >= threshold
    starts = np.where(np.diff(above.astype(int)) == 1)[0] + 1
    ends   = np.where(np.diff(above.astype(int)) == -1)[0] + 1

    n = min(len(starts), len(ends))
    return [
        {"start": s, "end": e, "start_time": time[s]}
        for s, e in zip(starts[:n], ends[:n])
    ]

# ======================================================
# EXTRACT PUSH WAVEFORMS
# ======================================================
def extract_waves(df, pushes, t0, t1):
    waves = []
    for p in pushes:
        if t0 <= p["start_time"] <= t1:
            t = df["time"].values[p["start"]:p["end"]]
            y = df["torque"].values[p["start"]:p["end"]]
            if len(y) > 10:
                waves.append({"t": t - t[0], "y": y})
    return waves

# ======================================================
# MEAN ± SD (TIME)
# ======================================================
def mean_sd_time(waves, n=200):
    if len(waves) == 0:
        return None, None, None
    max_t = max(w["t"][-1] for w in waves)
    t_common = np.linspace(0, max_t, n)
    Y = np.array([np.interp(t_common, w["t"], w["y"]) for w in waves])
    return t_common, Y.mean(axis=0), Y.std(axis=0)

# ======================================================
# MEAN ± SD (% PUSH CYCLE)
# ======================================================
def mean_sd_percent(waves, n=200):
    if len(waves) == 0:
        return None, None, None
    x_common = np.linspace(0, 100, n)
    Y = []
    for w in waves:
        x_old = np.linspace(0, 100, len(w["y"]))
        Y.append(np.interp(x_common, x_old, w["y"]))
    Y = np.array(Y)
    return x_common, Y.mean(axis=0), Y.std(axis=0)

# ======================================================
# PUSH IMPULSE
# ======================================================
def compute_push_impulse(time, torque, s, e):
    """Torque impulse (Nm·s)"""
    return np.trapezoid(torque[s:e], time[s:e])

def impulse_stats(df, pushes, t0, t1):
    impulses = []
    for p in pushes:
        if t0 <= p["start_time"] <= t1:
            impulses.append(
                compute_push_impulse(
                    df["time"].values,
                    df["torque"].values,
                    p["start"],
                    p["end"]
                )
            )
    if len(impulses) < 2:
        return np.nan, np.nan
    return np.mean(impulses), np.std(impulses, ddof=1)

# ======================================================
# LOAD DATA
# ======================================================
file = "30Sec_baseline.xlsx"
left  = pd.read_excel(file, sheet_name="Ergo_Left")
right = pd.read_excel(file, sheet_name="Ergo_Right")

for df in (left, right):
    df["time"]  = pd.to_numeric(df["time"], errors="coerce")
    df["force"] = pd.to_numeric(df["force"], errors="coerce")
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

fs = 1 / np.mean(np.diff(left["time"]))

for df in (left, right):
    df["force_filt"] = butter_lowpass(df["force"].values, fs)
    df["torque"] = df["force_filt"] * wheel_radius

# ======================================================
# DETECT PUSHES
# ======================================================
L_pushes = detect_pushes(left["time"].values, left["torque"].values, push_threshold)
R_pushes = detect_pushes(right["time"].values, right["torque"].values, push_threshold)

# ======================================================
# PLOTTING
# ======================================================
fig, axes = plt.subplots(len(cases), 2, figsize=(16, 14), sharey=True)

for i, (label, t0, t1) in enumerate(cases):

    L_waves = extract_waves(left,  L_pushes, t0, t1)
    R_waves = extract_waves(right, R_pushes, t0, t1)

    # ----- TIME DOMAIN -----
    tL, Lm_t, Lsd_t = mean_sd_time(L_waves)
    tR, Rm_t, Rsd_t = mean_sd_time(R_waves)

    ax = axes[i, 0]
    if tL is not None:
        ax.plot(tL, Lm_t, color="red", label="Left mean")
        ax.fill_between(tL, Lm_t - Lsd_t, Lm_t + Lsd_t,
                        color="red", alpha=0.25)
    if tR is not None:
        ax.plot(tR, Rm_t, color="blue", label="Right mean")
        ax.fill_between(tR, Rm_t - Rsd_t, Rm_t + Rsd_t,
                        color="blue", alpha=0.25)

    L_imp, L_imp_sd = impulse_stats(left, L_pushes, t0, t1)
    R_imp, R_imp_sd = impulse_stats(right, R_pushes, t0, t1)

    ax.text(
        0.02, 0.95,
        f"Left : {L_imp:.2f} ± {L_imp_sd:.2f} Nm·s\n"
        f"Right: {R_imp:.2f} ± {R_imp_sd:.2f} Nm·s",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
    )

    ax.set_title(f"{label} — Torque vs Time")
    ax.set_xlabel("Time from push start (s)")
    ax.set_ylabel("Torque (Nm)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ----- % PUSH CYCLE -----
    pL, Lm_p, Lsd_p = mean_sd_percent(L_waves)
    pR, Rm_p, Rsd_p = mean_sd_percent(R_waves)

    ax = axes[i, 1]
    if pL is not None:
        ax.plot(pL, Lm_p, color="red", label="Left mean")
        ax.fill_between(pL, Lm_p - Lsd_p, Lm_p + Lsd_p,
                        color="red", alpha=0.25)
    if pR is not None:
        ax.plot(pR, Rm_p, color="blue", label="Right mean")
        ax.fill_between(pR, Rm_p - Rsd_p, Rm_p + Rsd_p,
                        color="blue", alpha=0.25)

    ax.text(
        0.02, 0.95,
        f"Left : {L_imp:.2f} ± {L_imp_sd:.2f} Nm·s\n"
        f"Right: {R_imp:.2f} ± {R_imp_sd:.2f} Nm·s",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
    )

    ax.set_title(f"{label} — Torque vs % Push Cycle")
    ax.set_xlabel("Push cycle (%)")
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()