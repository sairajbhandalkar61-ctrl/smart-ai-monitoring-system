# 🚀 Smart AI Monitoring System

An end-to-end AI-powered system that performs real-time crowd detection and activity prediction using Computer Vision, Machine Learning, and Deep Learning.

---

## 📌 Overview

This project demonstrates a complete AI pipeline that captures live video, detects people using OpenCV, and predicts crowd activity levels using a trained Deep Learning model.

The system provides real-time analytics, insights, and visualization through an interactive Streamlit dashboard.

---

## 🎯 Key Features

- Real-time webcam-based people detection (OpenCV)  
- Activity classification: Low / Moderate / High  
- Deep Learning model (ANN using TensorFlow/Keras)  
- Feature engineering (count, time, movement)  
- Confidence score for predictions  
- Live graph of crowd activity  
- FPS (performance monitoring)  
- AI-generated insights  
- Interactive dashboard using Streamlit  

---

## 🧠 Tech Stack

- Python  
- OpenCV  
- Scikit-learn  
- TensorFlow / Keras  
- Pandas, NumPy  
- Streamlit  

---

## 📁 Project Structure

smart-ai-monitoring/
│── app.py                 
│── detection.py           
│── ml_model.py            
│── llm.py                 
│
│── models/
│     ├── dl_model.h5      
│     ├── scaler.pkl       
│     ├── label_encoder.pkl
│
│── training/
│     ├── generate_data.py 
│     ├── features.py      
│     ├── train_dl_model.py
│
│── README.md

---

## ⚙️ Installation

git clone https://github.com/your-username/smart-ai-monitoring.git  
cd smart-ai-monitoring  
pip install -r requirements.txt  

---

## ▶️ Run the Application

python -m streamlit run app.py  

Open in browser:  
http://localhost:8501  

---

## 🧪 Model Workflow

1. Data Collection  
   - Real-time camera input or synthetic data  

2. Feature Engineering  
   - count (number of people)  
   - hour (time-based feature)  
   - count_diff (movement)  

3. Model Training  
   - Machine Learning (optional)  
   - Deep Learning (ANN using TensorFlow)  

4. Prediction  
   - Low  
   - Moderate  
   - High  

---

## 📊 Output

- Real-time people count  
- Activity prediction  
- Confidence score  
- FPS performance  
- Live graph visualization  
- AI-generated insights  

---

## 🧠 Example Use Cases

- Smart surveillance systems  
- Crowd monitoring  
- Public safety  
- Retail analytics  

---

## 🔥 Future Improvements

- Replace Haar Cascade with YOLO (Deep Learning detection)  
- Cloud deployment (AWS / GCP / Streamlit Cloud)  
- Improve model accuracy with more data  
- Multi-camera support  

---

## 🧑‍💻 Author

Sairaj Bhandalkar
AI/ML Engineer  

---

## ⭐ Support

If you like this project, give it a star on GitHub!
