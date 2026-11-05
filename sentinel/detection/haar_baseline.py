import cv2
import numpy as np
from typing import List
from .base import BaseDetector, Detection

class HaarBaselineDetector(BaseDetector):
    """
    Empirical baseline detector using OpenCV Haar Cascades
    (Frontal Face, Profile Face, Upper Body) with NMS fusion.
    """
    def __init__(self, score_thresh: float = 0.5, nms_thresh: float = 0.4):
        self.score_thresh = score_thresh
        self.nms_thresh = nms_thresh
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.profile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_profileface.xml'
        )
        self.upperbody_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_upperbody.xml'
        )

    @property
    def model_name(self) -> str:
        return "HaarCascade-MultiScale-Baseline"

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if frame is None or frame.size == 0:
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        candidate_boxes = []
        scores = []

        # 1. Frontal faces
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=3, minSize=(25, 25))
        for (x, y, w, h) in faces:
            candidate_boxes.append([int(x), int(y), int(w), int(h)])
            scores.append(0.95)

        # 2. Profile faces
        profiles = self.profile_cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=3, minSize=(25, 25))
        for (x, y, w, h) in profiles:
            candidate_boxes.append([int(x), int(y), int(w), int(h)])
            scores.append(0.90)

        # 3. Upper body
        bodies = self.upperbody_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=2, minSize=(40, 40))
        for (x, y, w, h) in bodies:
            candidate_boxes.append([int(x), int(y), int(w), int(h)])
            scores.append(0.85)

        detections = []
        if len(candidate_boxes) > 0:
            indices = cv2.dnn.NMSBoxes(candidate_boxes, scores, self.score_thresh, self.nms_thresh)
            if len(indices) > 0:
                for idx in indices.flatten():
                    x, y, w, h = candidate_boxes[idx]
                    detections.append(Detection(
                        x1=x, y1=y, x2=x + w, y2=y + h,
                        score=scores[idx],
                        class_id=1,
                        class_name="person_haar"
                    ))

        return detections
