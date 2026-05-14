"""Tests for src/behavior.py — behavior detection with synthetic data."""

import pytest
from collections import deque
from types import SimpleNamespace

from src.behavior import BehaviorAnalyzer, BehaviorType
from src.roi import ROIManager


def make_track(track_id, cx, cy, history=None):
    """Create a mock Track-like object."""
    t = SimpleNamespace()
    t.track_id = track_id
    t.bbox = (cx - 10, cy - 20, cx + 10, cy + 20)
    t.centroid = (cx, cy)
    t.history = deque(history or [(cx, cy)], maxlen=90)
    return t


@pytest.fixture
def roi_manager():
    """ROI manager with one counting and one restricted zone."""
    return ROIManager([
        {
            "name": "gate",
            "type": "counting",
            "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "crowd_threshold": 5,
        },
        {
            "name": "restricted",
            "type": "restricted",
            "polygon": [[200, 200], [300, 200], [300, 300], [200, 300]],
        },
    ])


class TestCrowdSurge:
    def test_surge_detected(self, roi_manager):
        """Count jump >= surge_delta should trigger a surge event."""
        analyzer = BehaviorAnalyzer(fps=30, surge_delta=3, surge_window_sec=1.0)

        # Frame 1: 1 person in gate
        tracks = [make_track(1, 50, 50)]
        counts = {"gate": 1, "restricted": 0}
        events = analyzer.analyze(tracks, counts, roi_manager)
        assert not any(e.behavior_type == BehaviorType.CROWD_SURGE for e in events)

        # Frame 2: jump to 5 persons
        tracks = [make_track(i, 50, 50) for i in range(1, 6)]
        counts = {"gate": 5, "restricted": 0}
        events = analyzer.analyze(tracks, counts, roi_manager)
        surges = [e for e in events if e.behavior_type == BehaviorType.CROWD_SURGE]
        assert len(surges) == 1

    def test_no_surge_below_delta(self, roi_manager):
        analyzer = BehaviorAnalyzer(fps=30, surge_delta=10)
        counts = {"gate": 1, "restricted": 0}
        analyzer.analyze([], counts, roi_manager)
        counts = {"gate": 3, "restricted": 0}
        events = analyzer.analyze([], counts, roi_manager)
        assert not any(e.behavior_type == BehaviorType.CROWD_SURGE for e in events)


class TestIntrusion:
    def test_new_entry_triggers_intrusion(self, roi_manager):
        """A track entering a restricted zone should trigger intrusion."""
        analyzer = BehaviorAnalyzer(fps=30)

        # Frame 1: no one in restricted zone
        events = analyzer.analyze([], {"gate": 0, "restricted": 0}, roi_manager)
        assert len(events) == 0

        # Frame 2: track 1 enters restricted zone
        tracks = [make_track(1, 250, 250)]
        counts = {"gate": 0, "restricted": 1}
        events = analyzer.analyze(tracks, counts, roi_manager)
        intrusions = [e for e in events if e.behavior_type == BehaviorType.INTRUSION]
        assert len(intrusions) == 1

    def test_same_track_no_repeat(self, roi_manager):
        """Same track staying in zone should not re-trigger within cooldown."""
        analyzer = BehaviorAnalyzer(fps=30, intrusion_cooldown_sec=10.0)

        tracks = [make_track(1, 250, 250)]
        counts = {"gate": 0, "restricted": 1}
        analyzer.analyze(tracks, counts, roi_manager)  # first entry

        # Same track, next frame
        events = analyzer.analyze(tracks, counts, roi_manager)
        intrusions = [e for e in events if e.behavior_type == BehaviorType.INTRUSION]
        assert len(intrusions) == 0


class TestLoitering:
    def test_loitering_after_threshold(self, roi_manager):
        """Track in restricted zone for loiter_time_sec should trigger."""
        fps = 10
        loiter_sec = 1.0  # 10 frames at 10 fps
        analyzer = BehaviorAnalyzer(fps=fps, loiter_time_sec=loiter_sec)

        tracks = [make_track(1, 250, 250)]
        counts = {"gate": 0, "restricted": 1}

        loiter_event_found = False
        for _ in range(15):  # run more than threshold frames
            events = analyzer.analyze(tracks, counts, roi_manager)
            if any(e.behavior_type == BehaviorType.LOITERING for e in events):
                loiter_event_found = True
                break

        assert loiter_event_found, "Loitering should have been detected"
