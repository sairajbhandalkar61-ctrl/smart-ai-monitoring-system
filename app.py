import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import streamlit as st
import cv2
import time
import numpy as np

from detection import detect_people
from ml_model import predict_activity_details
from llm import generate_insight

st.set_page_config(page_title="Smart AI Monitoring System - SENTINEL AI", layout="wide")

st.title("🚀 Smart AI Monitoring System — SENTINEL AI")
st.markdown("Real-time crowd detection, movement tracking, and Deep Learning ANN activity classification.")

# Session state
if "run" not in st.session_state:
    st.session_state.run = False
if "prev_count" not in st.session_state:
    st.session_state.prev_count = 0

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("▶ Start Camera"):
        st.session_state.run = True
with col2:
    if st.button("■ Stop Camera"):
        st.session_state.run = False

# Layout placeholders
frame_placeholder = st.empty()
metrics_placeholder = st.empty()

def get_camera_source():
    """Try local webcam with non-blocking check, or fallback to simulated video feed."""
    for i in [0, 1]:
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
        if cap is not None and cap.isOpened():
            ret, _ = cap.read()
            if ret:
                return cap
            cap.release()
    return None

sample_img_path = os.path.join(os.path.dirname(__file__), "static", "surveillance_sample.jpg")
if not os.path.exists(sample_img_path):
    sample_img_path = os.path.join(os.path.dirname(__file__), "surveillance_sample.jpg")

if st.session_state.run:
    cap = get_camera_source()
    is_simulation = cap is None

    if is_simulation:
        st.info("ℹ️ No hardware webcam detected. Running in High-Definition Surveillance Feed mode.")

    while st.session_state.run:
        if not is_simulation:
            ret, frame = cap.read()
            if not ret:
                st.warning("Webcam frame unavailable. Switching to surveillance feed.")
                is_simulation = True
                continue
            frame = cv2.flip(frame, 1)
        else:
            if os.path.exists(sample_img_path):
                frame = cv2.imread(sample_img_path)
            else:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Surveillance Feed", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Detection with dual-mode fallback
        frame, count = detect_people(frame)

        # Movement feature
        count_diff = count - st.session_state.prev_count
        st.session_state.prev_count = count

        # Prediction via retrained multi-class ANN model
        details = predict_activity_details(count, count_diff)
        activity = details["activity"]
        confidence = details["confidence"]
        movement = details["movement"]

        # Insight
        insight = generate_insight(activity, count, movement)

        # Render video frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, use_container_width=True)

        # Render KPI metrics
        with metrics_placeholder.container():
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("👥 Detected Faces", count, f"{count_diff:+d}")
            m2.metric("📊 Activity Level", activity)
            m3.metric("🎯 ANN Confidence", f"{confidence:.1f}%")
            m4.metric("🏃 Movement Level", movement)
            st.info(f"🤖 **AI Insight:** {insight}")

        time.sleep(0.1)

    if cap is not None:
        cap.release()
