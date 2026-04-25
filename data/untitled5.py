import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df = pd.read_excel("60m_push_breakdown.xlsx")

# normalise dash (important for your file)
df["distance_band"] = (
    df["distance_band"]
    .astype(str)
    .str.replace("–", "-", regex=False)
    .str.replace("−", "-", regex=False)
)

# --------------------------------------------------
# FILTER: cycle length components, 0–10 m, two reps
# --------------------------------------------------
df_len = df[
    (df["distance_band"] == "0-10") &
    (df["metric_key"].isin(["push_length", "rolling_length"])) &
    (df["trial_id"].isin(["60m_1", "60m_3"]))
].copy()

# --------------------------------------------------
# PREP DATA PER REP
# --------------------------------------------------
reps = ["60m_1", "60m_3"]
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5))

for i, rep in enumerate(reps):
    r = df_len[df_len["trial_id"] == rep]

    # use cycle_no directly – no reindexing
    cycles = sorted(r["cycle_no"].unique())
    x = np.array(cycles) + (i - 0.5) * width

    push = (
        r[r["metric_key"] == "push_length"]
        .sort_values("cycle_no")["value"]
        .values
    )

    roll = (
        r[r["metric_key"] == "rolling_length"]
        .sort_values("cycle_no")["value"]
        .values
    )

    ax.bar(
        x,
        push,
        width,
        label=f"Push – {rep}"
    )

    ax.bar(
        x,
        roll,
        width,
        bottom=push,
        label=f"Rolling – {rep}"
    )

# --------------------------------------------------
# FORMAT
# --------------------------------------------------
ax.set_xlabel("Cycle")
ax.set_ylabel("Distance (m)")
ax.set_title("Cycle Length Breakdown (0–10 m)")
ax.set_xticks(sorted(df_len["cycle_no"].unique()))
ax.legend()
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.show()
