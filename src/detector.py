"""Person detection module using YOLOv8.

Wraps the Ultralytics YOLO model to detect persons in video frames,
returning structured Detection objects for downstream processing.
"""

from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO


@dataclass
class Detection:
    """A single person detection.

    Attributes:
        bbox: (x1, y1, x2, y2) bounding box in pixel coordinates.
        confidence: Detection confidence score in [0, 1].
    """

    bbox: tuple[float, float, float, float]
    confidence: float


class PersonDetector:
    """YOLOv8-based person detector.

    Attributes:
        model: Loaded YOLO model instance.
        conf: Minimum confidence threshold.
        device: Inference device string.
    """

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        conf: float = 0.4,
        device: str = "auto",
    ):
        """Initialize the detector.

        Args:
            model_path: Path to YOLO weights or model name (auto-downloads).
            conf: Minimum confidence to keep a detection.
            device: Device string — "cpu", "cuda:0", "mps", or "auto".
        """
        # Resolve "auto" to let ultralytics pick best available device
        self.device = None if device == "auto" else device
        self.conf = conf
        self.model = YOLO(model_path)

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Run person detection on a single frame.

        Args:
            frame: BGR image as a NumPy array (H, W, 3).

        Returns:
            List of Detection objects, filtered to persons only.
        """
        results = self.model.predict(
            frame,
            conf=self.conf,
            device=self.device,
            classes=[0],  # COCO class 0 = person
            verbose=False,
        )

        detections = []
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            detections.append(Detection(bbox=(x1, y1, x2, y2), confidence=conf))

        return detections
