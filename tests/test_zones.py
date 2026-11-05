import pytest
from sentinel.detection.base import Detection
from sentinel.tracking.tracker import Track
from sentinel.occupancy.zones import MonitoringZone, ZoneManager

def test_zone_point_inclusion():
    pts = [(0, 0), (200, 0), (200, 200), (0, 200)]
    zone = MonitoringZone("z1", "Test Zone", pts, capacity=5)
    
    # Track inside zone: center (100, 100)
    d_in = Detection(80, 80, 120, 120, score=0.9)
    t_in = Track(d_in)

    # Track outside zone: center (300, 300)
    d_out = Detection(280, 280, 320, 320, score=0.9)
    t_out = Track(d_out)

    count = zone.update_occupancy([t_in, t_out])
    assert count == 1
    assert zone.density_percentage == 20.0  # 1/5 = 20%
