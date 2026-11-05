import numpy as np
import pytest
from sentinel.quality.image_quality import ImageQualityAssessor

def test_quality_on_empty_frame():
    assessor = ImageQualityAssessor()
    res = assessor.assess(None)
    assert res["valid"] is False
    assert res["reliable"] is False

def test_quality_on_normal_frame():
    assessor = ImageQualityAssessor()
    # Create textured test frame (gradient + noise)
    frame = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
    res = assessor.assess(frame)
    assert res["valid"] is True
    assert res["brightness"] > 30.0

def test_quality_on_dark_frame():
    assessor = ImageQualityAssessor(min_brightness=40.0)
    dark_frame = np.zeros((480, 640, 3), dtype=np.uint8) + 10
    res = assessor.assess(dark_frame)
    assert res["valid"] is True
    assert res["is_dark"] is True
    assert res["reliable"] is False
