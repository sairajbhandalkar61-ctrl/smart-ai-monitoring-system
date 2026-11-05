import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.utils import to_categorical
import joblib

# Load dataset
df = pd.read_csv("training/processed_data.csv")

# ⚠️ Ensure multiple classes exist
print("Class distribution:")
print(df["activity"].value_counts())

# Features and target
X = df[["count", "hour", "count_diff"]]
y = df["activity"]

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# One-hot encoding
num_classes = len(np.unique(y_encoded))
y_categorical = to_categorical(y_encoded, num_classes=num_classes)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_categorical, test_size=0.2, random_state=42
)

# Build ANN model
model = Sequential([
    Input(shape=(3,)),
    Dense(16, activation='relu'),
    Dense(8, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train model
model.fit(X_train, y_train, epochs=20, batch_size=8, verbose=1)

# Evaluate
loss, accuracy = model.evaluate(X_test, y_test)
print(f"DL Model Accuracy: {accuracy:.2f}")

# Save
model.save("models/dl_model.h5")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(le, "models/label_encoder.pkl")

print("✅ Deep Learning model saved successfully")