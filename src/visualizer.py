"""Real-time visualization module.

Draws bounding boxes, track IDs, centroid trails, ROI overlays,
crowd counts, and alert banners on video frames.
"""

import cv2
import numpy as np


# --- Color palette (BGR) ---
COLOR_BBOX = (0, 255, 0)         # Green boxes
COLOR_TRACK_TRAIL = (255, 200, 0)  # Cyan-ish trail
COLOR_ROI_COUNTING = (255, 255, 0)  # Cyan ROI
COLOR_ROI_RESTRICTED = (0, 0, 255)  # Red ROI
COLOR_ALERT_BG = (0, 0, 180)     # Dark red banner
COLOR_TEXT = (255, 255, 255)      # White text


class Visualizer:
    """Annotates frames with detection, tracking, and alert overlays.

    Attributes:
        display: Whether to show frames in an OpenCV window.
    """

    def __init__(self, display: bool = True):
        """Initialize the visualizer.

        Args:
            display: If True, show annotated frames in a GUI window.
        """
        self.display = display

    def render(
        self,
        frame: np.ndarray,
        tracks: list,
        roi_manager,
        roi_counts: dict[str, int],
        alert_messages: list[str],
    ) -> np.ndarray:
        """Draw all annotations on a copy of the frame.

        Args:
            frame: Original BGR frame.
            tracks: List of Track objects.
            roi_manager: ROIManager with zone definitions.
            roi_counts: Dict of zone_name -> count.
            alert_messages: List of alert strings to display as banners.

        Returns:
            Annotated frame (does not modify the original).
        """
        annotated = frame.copy()

        self._draw_rois(annotated, roi_manager, roi_counts)
        self._draw_tracks(annotated, tracks)
        self._draw_alerts(annotated, alert_messages)

        if self.display:
            cv2.imshow("Crowd Analysis", annotated)

        return annotated

    # ------------------------------------------------------------------- #
    # ROI overlay
    # ------------------------------------------------------------------- #
    def _draw_rois(self, frame, roi_manager, roi_counts):
        """Draw ROI polygons with semi-transparent fills and count labels."""
        overlay = frame.copy()

        for zone in roi_manager.zones:
            pts = np.array(zone.polygon, dtype=np.int32)
            color = (
                COLOR_ROI_COUNTING
                if zone.zone_type == "counting"
                else COLOR_ROI_RESTRICTED
            )

            # Semi-transparent fill
            cv2.fillPoly(overlay, [pts], color)

            # Border
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)

            # Label: zone name + count
            count = roi_counts.get(zone.name, 0)
            label = f"{zone.name}: {count}"
            if zone.crowd_threshold is not None:
                label += f"/{zone.crowd_threshold}"

            # Position label at top vertex
            label_pos = tuple(pts[0])
            cv2.putText(
                frame,
                label,
                (label_pos[0], label_pos[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                COLOR_TEXT,
                2,
            )

        # Blend overlay
        cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

    # ------------------------------------------------------------------- #
    # Bounding boxes, IDs, trails
    # ------------------------------------------------------------------- #
    def _draw_tracks(self, frame, tracks):
        """Draw bounding boxes, track IDs, and centroid trail lines."""
        for t in tracks:
            x1, y1, x2, y2 = [int(v) for v in t.bbox]

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_BBOX, 2)

            # Track ID label
            cv2.putText(
                frame,
                f"ID:{t.track_id}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                COLOR_BBOX,
                2,
            )

            # Centroid trail
            if len(t.history) > 1:
                pts = [(int(p[0]), int(p[1])) for p in t.history]
                for i in range(1, len(pts)):
                    cv2.line(frame, pts[i - 1], pts[i], COLOR_TRACK_TRAIL, 2)

    # ------------------------------------------------------------------- #
    # Alert banners
    # ------------------------------------------------------------------- #
    def _draw_alerts(self, frame, messages):
        """Draw alert messages as banners at the top of the frame."""
        y_offset = 30
        for msg in messages:
            # Background rectangle
            text_size = cv2.getTextSize(
                msg, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )[0]
            cv2.rectangle(
                frame,
                (10, y_offset - 20),
                (20 + text_size[0], y_offset + 5),
                COLOR_ALERT_BG,
                -1,
            )
            # Text
            cv2.putText(
                frame,
                msg,
                (15, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                COLOR_TEXT,
                2,
            )
            y_offset += 30

    def close(self):
        """Destroy any OpenCV windows."""
        if self.display:
            cv2.destroyAllWindows()
