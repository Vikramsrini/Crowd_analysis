"""Tests for src/tracker.py — mock-based tracking tests."""

import pytest
from unittest.mock import MagicMock, patch
from src.tracker import MultiTracker


class TestMultiTracker:
    """Test MultiTracker with mocked YOLO model."""

    @patch("src.tracker.YOLO", autospec=True)
    def test_update_with_tracks(self, mock_yolo_cls):
        """Tracker should return Track objects with IDs and centroids."""
        import numpy as np

        mock_model = MagicMock()

        # Mock tracking result
        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock(tolist=MagicMock(return_value=[10.0, 20.0, 50.0, 60.0]))]

        mock_id = MagicMock()
        mock_id.item.return_value = 1

        mock_boxes = MagicMock()
        mock_boxes.id = [mock_id]
        mock_boxes.__iter__ = MagicMock(return_value=iter([mock_box]))
        mock_boxes.__len__ = MagicMock(return_value=1)

        mock_result = MagicMock()
        mock_result.boxes = mock_boxes
        mock_model.track.return_value = [mock_result]

        tracker = MultiTracker(model=mock_model, tracker_type="bytetrack")
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tracks = tracker.update(frame)

        assert len(tracks) == 1
        assert tracks[0].track_id == 1
        assert tracks[0].centroid == (30.0, 40.0)

    @patch("src.tracker.YOLO", autospec=True)
    def test_update_no_tracks(self, mock_yolo_cls):
        """Tracker should return empty list when no IDs assigned."""
        import numpy as np

        mock_model = MagicMock()

        mock_boxes = MagicMock()
        mock_boxes.id = None

        mock_result = MagicMock()
        mock_result.boxes = mock_boxes
        mock_model.track.return_value = [mock_result]

        tracker = MultiTracker(model=mock_model)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tracks = tracker.update(frame)

        assert tracks == []
