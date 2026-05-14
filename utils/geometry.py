"""Geometry utilities for point-in-polygon tests and distance calculations.

This module provides lightweight geometric helpers used across the
crowd analysis pipeline (ROI counting, behavior speed calculation, etc.).
"""

import numpy as np
from shapely.geometry import Point, Polygon


def point_in_polygon(point: tuple[float, float], polygon: list[list[float]]) -> bool:
    """Check whether a 2-D point lies inside a polygon.

    Args:
        point: (x, y) coordinates of the point.
        polygon: List of [x, y] vertices defining the polygon.

    Returns:
        True if the point is inside (or on the boundary of) the polygon.
    """
    return Polygon(polygon).contains(Point(point))


def centroid(bbox: tuple[float, float, float, float]) -> tuple[float, float]:
    """Compute the centroid of an axis-aligned bounding box.

    Args:
        bbox: (x1, y1, x2, y2) top-left and bottom-right corners.

    Returns:
        (cx, cy) center coordinates.
    """
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def euclidean_distance(
    p1: tuple[float, float], p2: tuple[float, float]
) -> float:
    """Euclidean distance between two 2-D points.

    Args:
        p1: (x, y) first point.
        p2: (x, y) second point.

    Returns:
        Scalar distance.
    """
    return float(np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))


def bbox_iou(
    box_a: tuple[float, float, float, float],
    box_b: tuple[float, float, float, float],
) -> float:
    """Intersection-over-Union for two axis-aligned bounding boxes.

    Args:
        box_a: (x1, y1, x2, y2) first box.
        box_b: (x1, y1, x2, y2) second box.

    Returns:
        IoU value in [0, 1].
    """
    xa = max(box_a[0], box_b[0])
    ya = max(box_a[1], box_b[1])
    xb = min(box_a[2], box_b[2])
    yb = min(box_a[3], box_b[3])

    inter = max(0, xb - xa) * max(0, yb - ya)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - inter

    return inter / union if union > 0 else 0.0
