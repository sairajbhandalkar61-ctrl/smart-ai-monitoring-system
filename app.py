import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import streamlit as st
import cv2
import time

from detection import detect_people
from ml_model import predict_activity
from llm import generate_insight

st.set_page_config(page_title="Smart AI Monitoring System", layout="wide")

st.title("🚀 Smart AI Monitoring System")

# Buttons
start = st.button("Start Camera")
stop = st.button("Stop Camera")

FRAME_WINDOW = st.image([])

# Session state
if "run" not in st.session_state:
    st.session_state.run = False

if "prev_count" not in st.session_state:
    st.session_state.prev_count = 0

if start:
    st.session_state.run = True

if stop:
    st.session_state.run = False

# Try different backends automatically
def open_camera():
    for i in [0, 1, 2]:
        cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
        if cap.isOpened():
            return cap
    return None

cap = open_camera()

if st.session_state.run:
    if cap is None:
        st.error("❌ Camera not detected")
    else:
        while True:
            ret, frame = cap.read()

            if not ret:
                st.error("❌ Camera frame not captured")
                break

            frame = cv2.flip(frame, 1)

            # Detection
            frame, count = detect_people(frame)

            # Feature
            count_diff = count - st.session_state.prev_count
            st.session_state.prev_count = count

            # Prediction
            activity = predict_activity(count, count_diff)

            # Insight
            insight = generate_insight(activity, count)

            # Display
            FRAME_WINDOW.image(frame, channels="BGR")

            st.write(f"👥 Count: {count}")
            st.write(f"📊 Activity: {activity}")
            st.write(f"🤖 Insight: {insight}")

            time.sleep(0.1)

        cap.release()