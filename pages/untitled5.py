import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
df = pd.read_excel("60m_push_breakdown.xlsx")

# Filter to raw data ONLY
df_speed = df[
    (df["metric_key"] == "cycle_av_speed") &
    (df["trial_id"].isin(["60m_1", "60m_3"])) &
    (df["distance_band"] == "0-10")
]

# Print the raw values to the console
print("\nRAW VALUES FROM EXCEL (no processing):")
print(df_speed[["trial_id", "cycle_no", "value"]])

# Plot raw values
plt.figure(figsize=(7, 4))

for rep in ["60m_1", "60m_3"]:
    d = df_speed[df_speed["trial_id"] == rep]
    plt.plot(d["cycle_no"], d["value"], marker="o", label=rep)

plt.xlabel("cycle_no (raw from Excel)")
plt.ylabel("cycle_av_speed (raw value)")
plt.title("RAW Average Cycle Speed (0–10 m)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
