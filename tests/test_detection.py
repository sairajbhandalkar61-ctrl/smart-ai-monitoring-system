import numpy as np
import pytest
from sentinel.detection.haar_baseline import HaarBaselineDetector
from sentinel.detection.ssd_detector import SSDLitePersonDetector

def test_haar_detector_empty():
    det = HaarBaselineDetector()
    res = det.detect(None)
    assert res == []

def test_haar_detector_blank_frame():
    det = HaarBaselineDetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = det.detect(frame)
    assert isinstance(res, list)

def test_ssdlite_detector_blank_frame():
    det = SSDLitePersonDetector(confidence_threshold=0.5)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = det.detect(frame)
    assert isinstance(res, list)
    assert len(res) == 0  # Black frame contains no persons
