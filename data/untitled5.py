import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("60m_push_breakdown.xlsx")

# NORMALISE DASHES
df["distance_band"] = (
    df["distance_band"]
    .astype(str)
    .str.replace("–", "-", regex=False)
)

df_speed = df[
    (df["metric_key"] == "cycle_av_speed") &
    (df["trial_id"].isin(["60m_1", "60m_3"])) &
    (df["distance_band"] == "0-10")
]

print(df_speed[["trial_id", "cycle_no", "value"]])

plt.figure()
for rep in ["60m_1", "60m_3"]:
    d = df_speed[df_speed["trial_id"] == rep]
    plt.plot(d["cycle_no"], d["value"], marker="o", label=rep)

plt.legend()
plt.show()