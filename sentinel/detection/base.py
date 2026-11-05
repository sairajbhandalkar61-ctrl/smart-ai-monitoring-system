from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import numpy as np

class Detection:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, score: float, class_id: int = 1, class_name: str = "person"):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        self.score = float(score)
        self.class_id = class_id
        self.class_name = class_name

    @property
    def box_xywh(self) -> Tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1)

    @property
    def box_xyxy(self) -> Tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def center(self) -> Tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "box": [self.x1, self.y1, self.x2, self.y2],
            "score": round(self.score, 3),
            "class_name": self.class_name
        }

class BaseDetector(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect people in the frame and return a list of Detection objects."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
