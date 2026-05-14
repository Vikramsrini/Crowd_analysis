"""Abnormal behavior detection module.

Analyzes track histories and ROI counts to detect:
- Crowd surge (sudden count increase)
- Panic / stampede (high average speed)
- Loitering in restricted zones
- Unauthorized entry into restricted zones
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum

from utils.geometry import euclidean_distance, point_in_polygon


class BehaviorType(Enum):
    """Enumeration of detectable abnormal behaviors."""

    CROWD_SURGE = "crowd_surge"
    PANIC = "panic"
    LOITERING = "loitering"
    INTRUSION = "intrusion"


@dataclass
class BehaviorEvent:
    """A detected abnormal behavior event.

    Attributes:
        behavior_type: Type of behavior detected.
        zone_name: ROI zone where the event occurred.
        details: Human-readable description.
        track_ids: IDs of involved tracks (empty for zone-level events).
    """

    behavior_type: BehaviorType
    zone_name: str
    details: str
    track_ids: list[int]


class BehaviorAnalyzer:
    """Detects abnormal crowd behaviors from track data and ROI counts.

    Maintains internal state (count history, occupancy timers) across
    frames to enable temporal analysis.

    Attributes:
        fps: Video frame rate (for time-based thresholds).
        surge_delta: Minimum count jump to flag as surge.
        surge_window: Number of frames for surge detection window.
        panic_speed_thresh: Pixels/sec threshold for panic detection.
        panic_duration_frames: Consecutive frames above threshold to confirm.
        loiter_frames: Frames a track must stay in restricted zone.
        intrusion_cooldown_frames: Frames between duplicate intrusion alerts.
    """

    def __init__(
        self,
        fps: float,
        surge_delta: int = 10,
        surge_window_sec: float = 3.0,
        panic_speed_thresh: float = 200.0,
        panic_duration_frames: int = 15,
        loiter_time_sec: float = 30.0,
        intrusion_cooldown_sec: float = 5.0,
    ):
        """Initialize the behavior analyzer.

        Args:
            fps: Video frame rate for time↔frame conversion.
            surge_delta: Person-count jump threshold.
            surge_window_sec: Time window for surge detection.
            panic_speed_thresh: Average speed (px/sec) to flag panic.
            panic_duration_frames: Frames above speed to confirm panic.
            loiter_time_sec: Seconds in restricted zone to flag loitering.
            intrusion_cooldown_sec: Cooldown between intrusion alerts.
        """
        self.fps = fps

        # --- Surge ---
        self.surge_delta = surge_delta
        self.surge_window = int(surge_window_sec * fps)
        self._count_history: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max(2, int(surge_window_sec * fps)))
        )

        # --- Panic ---
        self.panic_speed_thresh = panic_speed_thresh
        self.panic_duration_frames = panic_duration_frames
        self._panic_counter: dict[str, int] = defaultdict(int)

        # --- Loitering ---
        self.loiter_frames = int(loiter_time_sec * fps)
        self._zone_occupancy: dict[tuple[int, str], int] = defaultdict(int)
        # track (track_id, zone_name) -> frame count inside

        # --- Intrusion ---
        self.intrusion_cooldown = int(intrusion_cooldown_sec * fps)
        self._intrusion_last_alert: dict[tuple[int, str], int] = defaultdict(
            lambda: -999999
        )
        self._prev_zone_tracks: dict[str, set[int]] = defaultdict(set)

        self._frame_idx = 0

    def analyze(
        self,
        tracks,
        roi_counts: dict[str, int],
        roi_manager,
    ) -> list[BehaviorEvent]:
        """Run all behavior checks for the current frame.

        Args:
            tracks: List of Track objects with .centroid, .history, .track_id.
            roi_counts: Dict of zone_name -> person count.
            roi_manager: ROIManager instance for zone lookups.

        Returns:
            List of BehaviorEvent objects detected this frame.
        """
        self._frame_idx += 1
        events: list[BehaviorEvent] = []

        events += self._check_surge(roi_counts, roi_manager)
        events += self._check_panic(tracks, roi_counts, roi_manager)
        events += self._check_loitering(tracks, roi_manager)
        events += self._check_intrusion(tracks, roi_manager)

        return events

    # --------------------------------------------------------------------- #
    # Surge: sudden count increase in a counting zone
    # --------------------------------------------------------------------- #
    def _check_surge(self, roi_counts, roi_manager) -> list[BehaviorEvent]:
        events = []
        for zone in roi_manager.get_counting_zones():
            name = zone.name
            count = roi_counts.get(name, 0)
            history = self._count_history[name]
            history.append(count)

            if len(history) >= 2:
                oldest = history[0]
                delta = count - oldest
                if delta >= self.surge_delta:
                    events.append(
                        BehaviorEvent(
                            behavior_type=BehaviorType.CROWD_SURGE,
                            zone_name=name,
                            details=f"Count surged by {delta} (from {oldest} to {count})",
                            track_ids=[],
                        )
                    )
        return events

    # --------------------------------------------------------------------- #
    # Panic: high average speed of tracks in a zone
    # --------------------------------------------------------------------- #
    def _check_panic(self, tracks, roi_counts, roi_manager) -> list[BehaviorEvent]:
        events = []
        for zone in roi_manager.get_counting_zones():
            name = zone.name
            zone_tracks = roi_manager.get_tracks_in_zone(name, tracks)

            if len(zone_tracks) < 3:
                self._panic_counter[name] = 0
                continue

            # Average speed of all tracks with enough history
            speeds = []
            for t in zone_tracks:
                if len(t.history) >= 2:
                    p1 = t.history[-2]
                    p2 = t.history[-1]
                    speed = euclidean_distance(p1, p2) * self.fps
                    speeds.append(speed)

            if not speeds:
                self._panic_counter[name] = 0
                continue

            avg_speed = sum(speeds) / len(speeds)

            if avg_speed >= self.panic_speed_thresh:
                self._panic_counter[name] += 1
            else:
                self._panic_counter[name] = 0

            if self._panic_counter[name] >= self.panic_duration_frames:
                events.append(
                    BehaviorEvent(
                        behavior_type=BehaviorType.PANIC,
                        zone_name=name,
                        details=f"Avg speed {avg_speed:.0f} px/s for {self._panic_counter[name]} frames",
                        track_ids=[t.track_id for t in zone_tracks],
                    )
                )
        return events

    # --------------------------------------------------------------------- #
    # Loitering: track stays in restricted zone too long
    # --------------------------------------------------------------------- #
    def _check_loitering(self, tracks, roi_manager) -> list[BehaviorEvent]:
        events = []
        active_keys = set()

        for zone in roi_manager.get_restricted_zones():
            zone_tracks = roi_manager.get_tracks_in_zone(zone.name, tracks)
            for t in zone_tracks:
                key = (t.track_id, zone.name)
                active_keys.add(key)
                self._zone_occupancy[key] += 1

                if self._zone_occupancy[key] == self.loiter_frames:
                    secs = self._zone_occupancy[key] / self.fps
                    events.append(
                        BehaviorEvent(
                            behavior_type=BehaviorType.LOITERING,
                            zone_name=zone.name,
                            details=f"Track {t.track_id} loitering for {secs:.1f}s",
                            track_ids=[t.track_id],
                        )
                    )

        # Reset occupancy for tracks that left restricted zones
        stale = [k for k in self._zone_occupancy if k not in active_keys]
        for k in stale:
            del self._zone_occupancy[k]

        return events

    # --------------------------------------------------------------------- #
    # Intrusion: new track enters restricted zone
    # --------------------------------------------------------------------- #
    def _check_intrusion(self, tracks, roi_manager) -> list[BehaviorEvent]:
        events = []
        for zone in roi_manager.get_restricted_zones():
            current_ids = set()
            for t in tracks:
                if point_in_polygon(t.centroid, zone.polygon):
                    current_ids.add(t.track_id)

            new_entries = current_ids - self._prev_zone_tracks[zone.name]
            for tid in new_entries:
                key = (tid, zone.name)
                frames_since = self._frame_idx - self._intrusion_last_alert[key]
                if frames_since >= self.intrusion_cooldown:
                    events.append(
                        BehaviorEvent(
                            behavior_type=BehaviorType.INTRUSION,
                            zone_name=zone.name,
                            details=f"Track {tid} entered restricted zone",
                            track_ids=[tid],
                        )
                    )
                    self._intrusion_last_alert[key] = self._frame_idx

            self._prev_zone_tracks[zone.name] = current_ids

        return events
