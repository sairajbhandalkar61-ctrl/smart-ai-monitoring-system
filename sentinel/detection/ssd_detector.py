import torch
import torchvision
from torchvision.transforms import functional as F
import numpy as np
import cv2
from typing import List
from .base import BaseDetector, Detection

class SSDLitePersonDetector(BaseDetector):
    """
    Modern lightweight Deep Learning person detector.
    Uses SSDLite320 with MobileNetV3 Large backbone pre-trained on COCO.
    Optimized for multi-core CPU execution.
    """
    def __init__(self, confidence_threshold: float = 0.40, nms_iou_threshold: float = 0.45):
        self.confidence_threshold = confidence_threshold
        self.nms_iou_threshold = nms_iou_threshold
        
        # Enforce CPU execution
        self.device = torch.device("cpu")
        weights = torchvision.models.detection.SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
        self.model = torchvision.models.detection.ssdlite320_mobilenet_v3_large(weights=weights)
        self.model.to(self.device)
        self.model.eval()

    @property
    def model_name(self) -> str:
        return "SSDLite320-MobileNetV3-CPU"

    @torch.no_grad()
    def detect(self, frame: np.ndarray) -> List[Detection]:
        if frame is None or frame.size == 0:
            return []

        h_orig, w_orig = frame.shape[:2]
        
        # Convert BGR (OpenCV) to RGB and normalize to [0, 1]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor_img = F.to_tensor(rgb_frame).unsqueeze(0).to(self.device)

        # Forward pass
        predictions = self.model(tensor_img)[0]
        
        boxes = predictions["boxes"].cpu().numpy()
        scores = predictions["scores"].cpu().numpy()
        labels = predictions["labels"].cpu().numpy()

        # COCO class 1 corresponds to 'person'
        person_mask = (labels == 1) & (scores >= self.confidence_threshold)
        
        candidate_boxes = boxes[person_mask]
        candidate_scores = scores[person_mask]

        if len(candidate_boxes) == 0:
            return []

        # Convert [x1, y1, x2, y2] to cv2 NMS format [x, y, w, h]
        cv_boxes = []
        for box in candidate_boxes:
            x1, y1, x2, y2 = box
            cv_boxes.append([int(x1), int(y1), int(x2 - x1), int(y2 - y1)])
        
        # Secondary NMS to filter dense overlapping boxes
        indices = cv2.dnn.NMSBoxes(cv_boxes, candidate_scores.tolist(), self.confidence_threshold, self.nms_iou_threshold)

        detections = []
        if len(indices) > 0:
            for idx in indices.flatten():
                x1, y1, x2, y2 = candidate_boxes[idx]
                score = float(candidate_scores[idx])
                
                # Clip coordinates to frame bounds
                x1 = max(0, min(int(x1), w_orig - 1))
                y1 = max(0, min(int(y1), h_orig - 1))
                x2 = max(0, min(int(x2), w_orig - 1))
                y2 = max(0, min(int(y2), h_orig - 1))

                detections.append(Detection(
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    score=score,
                    class_id=1,
                    class_name="person"
                ))

        return detections
