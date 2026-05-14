"""Integration test — verifies the pipeline components work together.

Note: This test requires no real video or YOLO model. It mocks the
video source and model to verify the data flow between modules.
"""

import pytest
from unittest.mock import MagicMock, patch
from collections import deque
from types import SimpleNamespace

import numpy as np

from src.roi import ROIManager
from src.behavior import BehaviorAnalyzer
from src.alert import AlertManager


def make_track(track_id, cx, cy, history=None):
    """Create a mock Track."""
    t = SimpleNamespace()
    t.track_id = track_id
    t.bbox = (cx - 10, cy - 20, cx + 10, cy + 20)
    t.centroid = (cx, cy)
    t.history = deque(history or [(cx, cy)], maxlen=90)
    return t


class TestPipelineIntegration:
    """End-to-end data flow test using synthetic data."""

    def test_full_pipeline_flow(self):
        """Simulate a single frame through ROI → Behavior → Alert."""
        # Setup ROI
        roi_mgr = ROIManager([
            {
                "name": "gate",
                "type": "counting",
                "polygon": [[0, 0], [200, 0], [200, 200], [0, 200]],
                "crowd_threshold": 3,
            },
            {
                "name": "restricted",
                "type": "restricted",
                "polygon": [[300, 300], [400, 300], [400, 400], [300, 400]],
            },
        ])

        behavior = BehaviorAnalyzer(fps=30, surge_delta=5, loiter_time_sec=1.0)
        alert_mgr = AlertManager(
            crowd_thresholds={"gate": 3},
            console_enabled=False,
            log_file=None,
        )

        # Simulate 5 people in counting zone → should trigger crowd alert
        tracks = [make_track(i, 50 + i * 10, 50) for i in range(5)]
        counts = roi_mgr.count(tracks)

        assert counts["gate"] == 5
        assert counts["restricted"] == 0

        events = behavior.analyze(tracks, counts, roi_mgr)
        alert_msgs = alert_mgr.process(counts, events)

        # Should have a crowd threshold alert
        assert any("CROWD ALERT" in msg for msg in alert_msgs)

    def test_restricted_zone_intrusion(self):
        """Track entering restricted zone should produce intrusion alert."""
        roi_mgr = ROIManager([
            {
                "name": "zone_a",
                "type": "restricted",
                "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
            },
        ])

        behavior = BehaviorAnalyzer(fps=30)
        alert_mgr = AlertManager(
            crowd_thresholds={},
            console_enabled=False,
            log_file=None,
        )

        # Frame 1: no tracks
        events = behavior.analyze([], {"zone_a": 0}, roi_mgr)
        alert_mgr.process({"zone_a": 0}, events)

        # Frame 2: intrusion
        tracks = [make_track(1, 50, 50)]
        counts = roi_mgr.count(tracks)
        events = behavior.analyze(tracks, counts, roi_mgr)
        alert_msgs = alert_mgr.process(counts, events)

        assert any("INTRUSION" in msg for msg in alert_msgs)
