"""Region of Interest (ROI) management and crowd counting.

Defines configurable polygon zones and counts persons inside each,
supporting both general counting ROIs and restricted zones.
"""

from dataclasses import dataclass

from utils.geometry import point_in_polygon


@dataclass
class ROIZone:
    """A named polygon zone with optional crowd threshold.

    Attributes:
        name: Human-readable zone name (e.g. "main_gate").
        zone_type: "counting" or "restricted".
        polygon: List of [x, y] vertices.
        crowd_threshold: Max crowd before alert (counting zones only).
    """

    name: str
    zone_type: str  # "counting" or "restricted"
    polygon: list[list[float]]
    crowd_threshold: int | None = None


class ROIManager:
    """Manages multiple ROI zones and counts persons in each.

    Attributes:
        zones: List of ROIZone definitions.
    """

    def __init__(self, roi_configs: list[dict]):
        """Load ROI zones from config dictionaries.

        Args:
            roi_configs: List of dicts from YAML config, each with
                keys: name, type, polygon, and optionally crowd_threshold.

        Raises:
            ValueError: If a polygon has fewer than 3 vertices.
        """
        self.zones: list[ROIZone] = []
        for cfg in roi_configs:
            poly = cfg["polygon"]
            if len(poly) < 3:
                raise ValueError(
                    f"ROI '{cfg['name']}' must have at least 3 vertices, got {len(poly)}"
                )
            self.zones.append(
                ROIZone(
                    name=cfg["name"],
                    zone_type=cfg["type"],
                    polygon=poly,
                    crowd_threshold=cfg.get("crowd_threshold"),
                )
            )

    def count(self, tracks) -> dict[str, int]:
        """Count persons inside each ROI zone.

        Args:
            tracks: List of Track objects with .centroid attribute.

        Returns:
            Dictionary mapping zone name to person count.
        """
        counts: dict[str, int] = {}
        for zone in self.zones:
            counts[zone.name] = sum(
                1 for t in tracks if point_in_polygon(t.centroid, zone.polygon)
            )
        return counts

    def get_tracks_in_zone(self, zone_name: str, tracks) -> list:
        """Get tracks whose centroids fall inside a specific zone.

        Args:
            zone_name: Name of the ROI zone.
            tracks: List of Track objects.

        Returns:
            Filtered list of tracks inside the zone.
        """
        zone = self._zone_by_name(zone_name)
        if zone is None:
            return []
        return [t for t in tracks if point_in_polygon(t.centroid, zone.polygon)]

    def get_counting_zones(self) -> list[ROIZone]:
        """Return zones of type 'counting'."""
        return [z for z in self.zones if z.zone_type == "counting"]

    def get_restricted_zones(self) -> list[ROIZone]:
        """Return zones of type 'restricted'."""
        return [z for z in self.zones if z.zone_type == "restricted"]

    def _zone_by_name(self, name: str) -> ROIZone | None:
        """Lookup a zone by name."""
        for z in self.zones:
            if z.name == name:
                return z
        return None
