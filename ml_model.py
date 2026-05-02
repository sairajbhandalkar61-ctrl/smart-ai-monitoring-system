import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from tensorflow.keras.models import load_model

dl_model = load_model("models/dl_model.h5")
scaler = joblib.load("models/scaler.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")

def predict_activity(count, count_diff):
    hour = datetime.now().hour

    features = pd.DataFrame([[count, hour, count_diff]],
                            columns=["count", "hour", "count_diff"])

    features_scaled = scaler.transform(features)

    prediction = dl_model.predict(features_scaled, verbose=0)
    predicted_class = np.argmax(prediction)

    return label_encoder.inverse_transform([predicted_class])[0]