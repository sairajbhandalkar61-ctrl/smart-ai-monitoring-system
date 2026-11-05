import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from tensorflow.keras.models import load_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "dl_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoder.pkl")

# Load trained artifacts
dl_model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoder = joblib.load(ENCODER_PATH)

def predict_activity_details(count: int, count_diff: int, hour: int = None):
    if hour is None:
        hour = datetime.now().hour

    features = pd.DataFrame([[count, hour, count_diff]],
                            columns=["count", "hour", "count_diff"])

    features_scaled = scaler.transform(features)
    prediction = dl_model.predict(features_scaled, verbose=0)[0]
    predicted_class_idx = int(np.argmax(prediction))
    predicted_label = str(label_encoder.inverse_transform([predicted_class_idx])[0])
    confidence = float(prediction[predicted_class_idx]) * 100

    probs = {}
    for idx, cls_name in enumerate(label_encoder.classes_):
        probs[str(cls_name)] = round(float(prediction[idx]) * 100, 1)

    abs_diff = abs(count_diff)
    if abs_diff >= 5:
        movement = "High"
    elif abs_diff >= 2:
        movement = "Medium"
    else:
        movement = "Low"

    return {
        "activity": predicted_label,
        "confidence": round(confidence, 1),
        "probabilities": probs,
        "movement": movement,
        "count": count,
        "count_diff": count_diff,
        "hour": hour
    }

def predict_activity(count: int, count_diff: int):
    details = predict_activity_details(count, count_diff)
    return details["activity"]
