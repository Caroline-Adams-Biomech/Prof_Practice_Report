import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# ======================================================
# PARAMETERS (LOCKED)
# ======================================================
wheel_radius = 0.34          # m
force_cutoff = 10.0          # Hz
filter_order = 4

# Constant threshold (baseline comparison)
torque_threshold = 1.0       # Nm

# Hybrid thresholds (biomechanically tuned)
start_thresh = 5.0           # Nm
end_thresh = 4.0             # Nm
slope_thresh = 20.0          # Nm/s

t_window_start = 15.0        # s
t_window_end = 25.0          # s

# ======================================================
# HELPER FUNCTIONS
# ======================================================
def butter_lowpass(signal_data, fs, cutoff, order):
    nyq = fs / 2.0
    b, a = butter(order, cutoff / nyq, btype="low")
    return filtfilt(b, a, signal_data)


def torque_gradient(torque, fs):
    """Compute dTorque/dt"""
    return np.gradient(torque) * fs


def extract_push_waveforms(time, torque, threshold):
    above = torque > threshold
    starts = np.where(np.diff(above.astype(int)) == 1)[0] + 1

    pushes = []
    for s in starts:
        e = s
        while e < len(torque) and torque[e] > threshold:
            e += 1

        pushes.append({
            "start_time": time[s],
            "t_rel": time[s:e] - time[s],
            "torque": torque[s:e]
        })

    return pushes


def detect_pushes_constant(time, torque, threshold):
    above = torque > threshold
    starts = np.where(np.diff(above.astype(int)) == 1)[0] + 1
    ends   = np.where(np.diff(above.astype(int)) == -1)[0] + 1

    n = min(len(starts), len(ends))
    starts = starts[:n]
    ends = ends[:n]

    pushes = []
    for s, e in zip(starts, ends):
        pushes.append({
            "start_time": time[s],
            "end_time": time[e],
            "duration": time[e] - time[s]
        })

    return pushes


def detect_pushes_hybrid(time, torque, fs,
                         start_thresh, end_thresh, slope_thresh):
    dTdt = torque_gradient(torque, fs)

    pushes = []
    in_push = False
    start_idx = None

    for i in range(len(torque)):
        if not in_push:
            if torque[i] >= start_thresh and dTdt[i] >= slope_thresh:
                in_push = True
                start_idx = i
        else:
            if torque[i] <= end_thresh and dTdt[i] <= 0:
                end_idx = i
                pushes.append({
                    "start_time": time[start_idx],
                    "end_time": time[end_idx],
                    "duration": time[end_idx] - time[start_idx]
                })
                in_push = False

    return pushes

# ======================================================
# LOAD DATA
# ======================================================
file = "30Sec_baseline.xlsx"
left = pd.read_excel(file, sheet_name="Ergo_Left")
right = pd.read_excel(file, sheet_name="Ergo_Right")

# ======================================================
# CLEAN & VALIDATE
# ======================================================
for df in [left, right]:
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["force"] = pd.to_numeric(df["force"], errors="coerce")

left = left.dropna(subset=["time", "force"]).reset_index(drop=True)
right = right.dropna(subset=["time", "force"]).reset_index(drop=True)

# ======================================================
# SAMPLING FREQUENCY
# ======================================================
fs = 1.0 / np.mean(np.diff(left["time"].values))
print(f"Sampling frequency: {fs:.1f} Hz")

# ======================================================
# FILTER & TORQUE
# ======================================================
left["force_filt"] = butter_lowpass(left["force"].values, fs, force_cutoff, filter_order)
right["force_filt"] = butter_lowpass(right["force"].values, fs, force_cutoff, filter_order)

left["torque_calc"] = left["force_filt"] * wheel_radius
right["torque_calc"] = right["force_filt"] * wheel_radius

time = left["time"].values
torque = left["torque_calc"].values

# ======================================================
# PUSH DETECTION (CONSTANT vs HYBRID)
# ======================================================
const_pushes = detect_pushes_constant(time, torque, torque_threshold)
hyb_pushes = detect_pushes_hybrid(
    time, torque, fs,
    start_thresh, end_thresh, slope_thresh
)

# Restrict to 15–25 s
const_15_25 = [p for p in const_pushes if t_window_start <= p["start_time"] <= t_window_end]
hyb_15_25 = [p for p in hyb_pushes if t_window_start <= p["start_time"] <= t_window_end]

# ======================================================
# QUANTITATIVE COMPARISON
# ======================================================
const_durs = np.array([p["duration"] for p in const_15_25])
hyb_durs = np.array([p["duration"] for p in hyb_15_25])

print("\n=== PUSH DURATION COMPARISON (15–25 s) ===")
print(f"Constant threshold (1 Nm): "
      f"{np.mean(const_durs):.3f} ± {np.std(const_durs):.3f} s")

print(f"Hybrid (5 Nm + slope):   "
      f"{np.mean(hyb_durs):.3f} ± {np.std(hyb_durs):.3f} s")

# ======================================================
# DIAGNOSTIC VISUALISATION
# ======================================================
mask = (time >= t_window_start) & (time <= t_window_end)

plt.figure(figsize=(9,4))
plt.plot(time[mask], torque[mask], linewidth=2, label="Torque")

# Overlay hybrid start/end markers
for p in hyb_15_25:
    plt.axvline(p["start_time"], color="green", linestyle="--", alpha=0.8)
    plt.axvline(p["end_time"], color="red", linestyle="--", alpha=0.8)

plt.title("Hybrid Push Detection Diagnostics (15–25 s)")
plt.xlabel("Time (s)")
plt.ylabel("Torque (Nm)")
plt.legend(["Torque", "Push start", "Push end"])
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()