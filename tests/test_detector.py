"""Tests for src/detector.py — mock-based detection tests."""

import pytest
from unittest.mock import MagicMock, patch
from src.detector import PersonDetector, Detection


class TestPersonDetector:
    """Test the PersonDetector using mocked YOLO model."""

    @patch("src.detector.YOLO")
    def test_detect_returns_detections(self, mock_yolo_cls):
        """Detector should return list of Detection objects."""
        import numpy as np

        # Mock YOLO model and its predict output
        mock_model = MagicMock()
        mock_yolo_cls.return_value = mock_model

        # Create mock box
        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock(tolist=MagicMock(return_value=[10.0, 20.0, 50.0, 60.0]))]
        mock_box.conf = [MagicMock(__float__=lambda self: 0.85)]

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]
        mock_model.predict.return_value = [mock_result]

        detector = PersonDetector(model_path="yolov8n.pt", conf=0.4)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect(frame)

        assert len(detections) == 1
        assert isinstance(detections[0], Detection)
        assert detections[0].bbox == (10.0, 20.0, 50.0, 60.0)

    @patch("src.detector.YOLO")
    def test_detect_empty_frame(self, mock_yolo_cls):
        """Detector should return empty list when no detections."""
        import numpy as np

        mock_model = MagicMock()
        mock_yolo_cls.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = []
        mock_model.predict.return_value = [mock_result]

        detector = PersonDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect(frame)

        assert detections == []
