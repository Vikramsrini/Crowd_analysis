"""Multi-object tracking module.

Uses Ultralytics built-in ByteTrack/BoT-SORT to assign persistent IDs
to detected persons across video frames, maintaining centroid history
for downstream behavior analysis.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field

import numpy as np
from ultralytics import YOLO

from utils.geometry import centroid


@dataclass
class Track:
    """A tracked individual across frames.

    Attributes:
        track_id: Unique persistent ID assigned by the tracker.
        bbox: Current (x1, y1, x2, y2) bounding box.
        centroid: Current (cx, cy) center position.
        history: Rolling deque of past centroid positions.
    """

    track_id: int
    bbox: tuple[float, float, float, float]
    centroid: tuple[float, float]
    history: deque = field(default_factory=deque)


class MultiTracker:
    """Wraps YOLO tracking to produce Track objects with centroid history.

    Attributes:
        model: YOLO model shared with the detector.
        tracker_type: "bytetrack.yaml" or "botsort.yaml".
        max_history: Maximum centroid history length per track.
        histories: Internal mapping of track_id -> deque of centroids.
    """

    def __init__(
        self,
        model: YOLO,
        tracker_type: str = "bytetrack",
        conf: float = 0.4,
        max_history: int = 90,
        device: str = "auto",
    ):
        """Initialize the tracker.

        Args:
            model: Pre-loaded YOLO model instance (shared with detector).
            tracker_type: "bytetrack" or "botsort".
            conf: Detection confidence threshold (passed to tracker).
            max_history: Number of past centroids to keep per track.
            device: Inference device string.
        """
        self.model = model
        self.tracker_config = f"{tracker_type}.yaml"
        self.conf = conf
        self.device = None if device == "auto" else device
        self.max_history = max_history
        self.histories: dict[int, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )

    def update(self, frame: np.ndarray) -> list[Track]:
        """Run detection + tracking on a frame.

        This method uses YOLO's built-in .track() which performs both
        detection and tracking in one call. For each tracked person,
        we update the centroid history.

        Args:
            frame: BGR image as a NumPy array (H, W, 3).

        Returns:
            List of active Track objects with updated histories.
        """
        results = self.model.track(
            frame,
            conf=self.conf,
            device=self.device,
            classes=[0],
            tracker=self.tracker_config,
            persist=True,
            verbose=False,
        )

        tracks: list[Track] = []
        boxes = results[0].boxes

        if boxes.id is None:
            # No tracks in this frame
            return tracks

        for box, track_id_tensor in zip(boxes, boxes.id):
            tid = int(track_id_tensor.item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            bbox = (x1, y1, x2, y2)
            cx, cy = centroid(bbox)

            # Update history
            self.histories[tid].append((cx, cy))

            tracks.append(
                Track(
                    track_id=tid,
                    bbox=bbox,
                    centroid=(cx, cy),
                    history=self.histories[tid],
                )
            )

        return tracks
