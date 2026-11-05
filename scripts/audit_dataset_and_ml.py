import os
import sys
import json
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'evidence', 'phase_02')
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("  SENTINEL AI — PHASE 2 DATASET & ML PIPELINE AUDIT SCRIPT")
print("=" * 60)

# -------------------------------------------------------------
# 1. RAW DATASET AUDIT (data.csv)
# -------------------------------------------------------------
data_path = os.path.join(os.path.dirname(__file__), '..', 'data.csv')
if not os.path.exists(data_path):
    print(f"[!] Error: data.csv not found at {data_path}")
    sys.exit(1)

df_raw = pd.read_csv(data_path)
print(f"[+] Loaded data.csv: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")

# Schema & dtypes
schema_info = {
    "rows": int(df_raw.shape[0]),
    "columns": list(df_raw.columns),
    "dtypes": {col: str(df_raw[col].dtype) for col in df_raw.columns},
    "null_counts": {col: int(df_raw[col].isnull().sum()) for col in df_raw.columns}
}
print(f"    Columns & Dtypes: {schema_info['dtypes']}")
print(f"    Missing values: {schema_info['null_counts']}")

# Exact duplicates
exact_dupes = int(df_raw.duplicated().sum())
print(f"    Exact duplicate rows: {exact_dupes}")

# Near duplicates on feature columns ('count')
count_counts = df_raw['count'].value_counts().to_dict()
print(f"    Count values distribution: {count_counts}")

# Label analysis
raw_labels = df_raw['activity'].value_counts().to_dict()
print(f"    Raw label distribution: {raw_labels}")

# Timestamps & Temporal Coverage
df_raw['datetime'] = pd.to_datetime(df_raw['time'], errors='coerce')
valid_dates = df_raw['datetime'].dropna()
df_raw['date_str'] = valid_dates.dt.date.astype(str)
df_raw['hour_int'] = valid_dates.dt.hour

date_counts = df_raw['date_str'].value_counts().to_dict()
hour_counts = df_raw['hour_int'].value_counts().to_dict()
print(f"    Date breakdown: {date_counts}")
print(f"    Hour breakdown: {hour_counts}")

# Temporal span and autocorrelation
if len(valid_dates) > 1:
    time_diffs = valid_dates.diff().dt.total_seconds().dropna()
    median_spacing = float(time_diffs.median())
    max_spacing = float(time_diffs.max())
    print(f"    Median time between samples: {median_spacing:.2f} seconds")
    print(f"    Max time gap between samples: {max_spacing:.2f} seconds ({max_spacing/3600:.2f} hours)")

# Autocorrelation of count
autocorr_1 = float(df_raw['count'].autocorr(lag=1))
autocorr_5 = float(df_raw['count'].autocorr(lag=5))
print(f"    Count autocorrelation (lag=1): {autocorr_1:.4f}")
print(f"    Count autocorrelation (lag=5): {autocorr_5:.4f}")

# Target Leakage check (deterministic dependency between count and activity)
leakage_check = pd.crosstab(df_raw['count'], df_raw['activity'])
print(f"    Crosstab (Count vs Activity):\n{leakage_check}")

# Save Summary Table
audit_summary = {
    "total_rows": int(len(df_raw)),
    "columns": list(df_raw.columns),
    "exact_duplicates": exact_dupes,
    "missing_values": schema_info['null_counts'],
    "count_value_counts": count_counts,
    "activity_value_counts": raw_labels,
    "dates": date_counts,
    "hours": hour_counts,
    "autocorrelation_lag_1": autocorr_1,
    "autocorrelation_lag_5": autocorr_5,
    "median_sample_interval_sec": median_spacing
}
with open(os.path.join(OUT_DIR, "dataset_audit_metrics.json"), "w") as f:
    json.dump(audit_summary, f, indent=2)

# Generate Distribution Plots
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# Plot 1: Count Distribution
axes[0].bar([str(k) for k in count_counts.keys()], list(count_counts.values()), color='#3b82f6', edgecolor='#1d4ed8')
axes[0].set_title("People Count Distribution in data.csv")
axes[0].set_xlabel("Count (Detected Persons)")
axes[0].set_ylabel("Frequency")
for k, v in count_counts.items():
    axes[0].text(str(k), v + 10, str(v), ha='center', fontweight='bold')

# Plot 2: Class Labels Distribution
axes[1].bar(list(raw_labels.keys()), list(raw_labels.values()), color='#10b981', edgecolor='#047857')
axes[1].set_title("Activity Class Labels in data.csv")
axes[1].set_xlabel("Activity Class")
axes[1].set_ylabel("Frequency")
for k, v in raw_labels.items():
    axes[1].text(k, v + 10, str(v), ha='center', fontweight='bold')

# Plot 3: Temporal Sample Intervals
axes[2].hist(np.clip(time_diffs, 0, 10), bins=20, color='#f59e0b', edgecolor='#b45309')
axes[2].set_title("Inter-Sample Time Delta Distribution (<=10s)")
axes[2].set_xlabel("Delta Time (seconds)")
axes[2].set_ylabel("Frequency")

plt.tight_layout()
fig_path = os.path.join(OUT_DIR, "dataset_audit_distributions.png")
fig.savefig(fig_path, dpi=200)
plt.close(fig)
print(f"[+] Saved audit plots to {fig_path}")

# -------------------------------------------------------------
# 2. PROCESSED DATASET AUDIT (processed_data.csv)
# -------------------------------------------------------------
proc_path = os.path.join(os.path.dirname(__file__), '..', 'training', 'processed_data.csv')
if os.path.exists(proc_path):
    df_proc = pd.read_csv(proc_path)
    print(f"\n[+] Loaded training/processed_data.csv: {df_proc.shape[0]} rows")
    print(f"    Content:\n{df_proc}")
    df_proc.to_csv(os.path.join(OUT_DIR, "processed_data_snapshot.csv"), index=False)

# -------------------------------------------------------------
# 3. SHIPPED MODEL ARTIFACTS AUDIT & GRID EVALUATION
# -------------------------------------------------------------
print("\n[+] Testing Shipped Model Artifacts under Grid Inputs...")
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'dl_model.h5')
scaler_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.pkl')
encoder_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'label_encoder.pkl')

model = tf.keras.models.load_model(model_path)
scaler = joblib.load(scaler_path)
le = joblib.load(encoder_path)

print(f"    LabelEncoder classes: {le.classes_}")
print(f"    Scaler mean: {scaler.mean_}, scale: {scaler.scale_}")
print(f"    Model output shape: {model.output_shape}")

# Run across varied input combinations (count 0..30, count_diff -5..5, hour 0..23)
test_inputs = [
    [0, 12, 0],
    [1, 18, 0],
    [2, 18, 1],
    [5, 14, 3],
    [12, 10, 2],
    [18, 18, 5],
    [25, 20, -4],
    [30, 22, 6]
]
grid_df = pd.DataFrame(test_inputs, columns=["count", "hour", "count_diff"])
grid_scaled = scaler.transform(grid_df)
raw_preds = model.predict(grid_scaled, verbose=0)

results = []
for i, row in grid_df.iterrows():
    pred_val = raw_preds[i]
    pred_idx = int(np.argmax(pred_val))
    pred_label = le.inverse_transform([pred_idx])[0]
    conf = float(pred_val[pred_idx]) * 100
    results.append({
        "count": int(row["count"]),
        "hour": int(row["hour"]),
        "count_diff": int(row["count_diff"]),
        "raw_output": [round(float(x), 4) for x in pred_val],
        "predicted_label": pred_label,
        "confidence_pct": round(conf, 2)
    })

res_df = pd.DataFrame(results)
print("    Grid Prediction Results:")
print(res_df.to_string())
res_df.to_csv(os.path.join(OUT_DIR, "shipped_model_grid_predictions.csv"), index=False)

# Check invariance
all_same_class = len(res_df['predicted_label'].unique()) == 1
all_100_conf = (res_df['confidence_pct'] == 100.0).all()
print(f"    Is output label invariant across all inputs? {all_same_class} (Always predicts '{res_df['predicted_label'].iloc[0]}')")
print(f"    Is confidence always exactly 100.0%? {all_100_conf}")

# -------------------------------------------------------------
# 4. ORIGINAL TRAINING PIPELINE REPRODUCTION (train_dl_model.py audit)
# -------------------------------------------------------------
print("\n[+] Reproducing Original Pipeline Logic on data.csv...")
# Replicate features.py logic
df_feat = df_raw.copy()
df_feat['hour'] = df_feat['datetime'].dt.hour.fillna(18).astype(int)
df_feat['count_diff'] = df_feat['count'].diff().fillna(0)

# Check what the label logic in training/features.py actually produces:
# if count >= 5: 'High' elif count >= 2: 'Moderate' else: 'Low'
def assign_activity(c):
    if c >= 5:
        return 'High'
    elif c >= 2:
        return 'Moderate'
    else:
        return 'Low'

df_feat['rule_activity'] = df_feat['count'].apply(assign_activity)
rule_dist = df_feat['rule_activity'].value_counts().to_dict()
print(f"    Features.py rule applied to data.csv yields: {rule_dist}")

print("=" * 60)
print("  PHASE 2 AUDIT COMPLETE. EVIDENCE COMMITTED TO evidence/phase_02/")
print("=" * 60)
