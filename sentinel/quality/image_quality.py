import cv2
import numpy as np
from typing import Dict, Any

class ImageQualityAssessor:
    """
    Assesses frame quality metrics to verify computer vision reliability.
    Computes blur score via Laplacian variance and brightness distribution.
    """
    def __init__(self, blur_threshold: float = 60.0, min_brightness: float = 30.0, max_brightness: float = 230.0):
        self.blur_threshold = blur_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness

    def assess(self, frame: np.ndarray) -> Dict[str, Any]:
        if frame is None or frame.size == 0:
            return {
                "valid": False,
                "blur_score": 0.0,
                "brightness": 0.0,
                "is_blurry": True,
                "is_dark": True,
                "is_overexposed": False,
                "status": "Frame Corrupted / Empty",
                "reliable": False
            }

        # Convert to grayscale for metric computation
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # 1. Blur via variance of Laplacian
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_blurry = laplacian_var < self.blur_threshold

        # 2. Mean brightness
        mean_brightness = float(np.mean(gray))
        is_dark = mean_brightness < self.min_brightness
        is_overexposed = mean_brightness > self.max_brightness

        # 3. Overall reliability determination
        reliable = True
        status_reasons = []

        if is_blurry:
            reliable = False
            status_reasons.append("High Blur")
        if is_dark:
            reliable = False
            status_reasons.append("Low Lighting")
        if is_overexposed:
            reliable = False
            status_reasons.append("Overexposed")

        if reliable:
            status = "Optimal Quality"
        else:
            status = "Poor Quality: " + ", ".join(status_reasons) + " — Manual Verification Required"

        return {
            "valid": True,
            "blur_score": round(laplacian_var, 2),
            "brightness": round(mean_brightness, 2),
            "is_blurry": is_blurry,
            "is_dark": is_dark,
            "is_overexposed": is_overexposed,
            "status": status,
            "reliable": reliable
        }
