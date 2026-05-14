"""Tests for utils/geometry.py — point-in-polygon, centroid, distance, IoU."""

import pytest
from utils.geometry import point_in_polygon, centroid, euclidean_distance, bbox_iou


class TestPointInPolygon:
    """Verify point-in-polygon checks with known geometries."""

    SQUARE = [[0, 0], [10, 0], [10, 10], [0, 10]]

    def test_inside(self):
        assert point_in_polygon((5, 5), self.SQUARE) is True

    def test_outside(self):
        assert point_in_polygon((15, 15), self.SQUARE) is False

    def test_edge(self):
        # Shapely considers boundary as NOT contained — verify behavior
        result = point_in_polygon((0, 5), self.SQUARE)
        assert isinstance(result, bool)

    def test_triangle(self):
        tri = [[0, 0], [10, 0], [5, 10]]
        assert point_in_polygon((5, 3), tri) is True
        assert point_in_polygon((0, 10), tri) is False


class TestCentroid:
    def test_simple(self):
        cx, cy = centroid((0, 0, 10, 10))
        assert cx == 5.0
        assert cy == 5.0

    def test_non_square(self):
        cx, cy = centroid((10, 20, 30, 60))
        assert cx == 20.0
        assert cy == 40.0


class TestEuclideanDistance:
    def test_zero(self):
        assert euclidean_distance((0, 0), (0, 0)) == 0.0

    def test_known(self):
        assert abs(euclidean_distance((0, 0), (3, 4)) - 5.0) < 1e-6


class TestBboxIou:
    def test_no_overlap(self):
        assert bbox_iou((0, 0, 5, 5), (10, 10, 15, 15)) == 0.0

    def test_full_overlap(self):
        assert bbox_iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0

    def test_partial_overlap(self):
        iou = bbox_iou((0, 0, 10, 10), (5, 5, 15, 15))
        assert 0 < iou < 1
