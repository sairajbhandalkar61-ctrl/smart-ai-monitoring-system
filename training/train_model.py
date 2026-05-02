import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Load processed data
df = pd.read_csv("training/processed_data.csv")

# Features (X) and target (y)
X = df[["count", "hour", "count_diff"]]
y = df["activity"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("Model Performance:")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "models/crowd_model.pkl")

print("✅ Model trained and saved in models/crowd_model.pkl")