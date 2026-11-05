import pandas as pd

df = pd.read_csv("data.csv")

df["time"] = pd.to_datetime(df["time"])
df["hour"] = df["time"].dt.hour
df["count_diff"] = df["count"].diff().fillna(0)

def label_activity(count):
    if count >= 5:
        return "High"
    elif count >= 2:
        return "Moderate"
    else:
        return "Low"

df["activity"] = df["count"].apply(label_activity)

df.to_csv("training/processed_data.csv", index=False)

print("Dataset created successfully")