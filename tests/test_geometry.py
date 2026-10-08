"""
tests/test_geometry.py  --  Round-trip tests for coordinate transforms.

Run with: pytest tests/test_geometry.py -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
import pytest
from core.models import Point
from core.geometry import (
    CoordTransform, distance, rotate_point, point_on_segment,
    closest_point_on_segment, estimate_scale_from_passives
)


class TestCoordTransform:
    def setup_method(self):
        self.xfm = CoordTransform(
            scale_px_per_mil=0.6,
            sheet_height_mils=8500,
            origin_px=(0.0, 0.0)
        )

    def test_px_to_mils_origin(self):
        mx, my = self.xfm.px_to_mils(0, 0)
        assert mx == pytest.approx(0.0)
        assert my == pytest.approx(8500.0)

    def test_round_trip_px(self):
        for px_x, px_y in [(100, 200), (0, 0), (500, 300), (60, 90)]:
            mx, my = self.xfm.px_to_mils(px_x, px_y)
            rx, ry = self.xfm.mils_to_px(mx, my)
            assert rx == pytest.approx(px_x, abs=1e-6)
            assert ry == pytest.approx(px_y, abs=1e-6)

    def test_round_trip_mils(self):
        for mx, my in [(4200, 3000), (0, 0), (8000, 1000)]:
            px_x, px_y = self.xfm.mils_to_px(mx, my)
            rmx, rmy = self.xfm.px_to_mils(px_x, px_y)
            assert rmx == pytest.approx(mx, abs=1e-6)
            assert rmy == pytest.approx(my, abs=1e-6)

    def test_y_flip(self):
        _, my_top = self.xfm.px_to_mils(0, 0)
        _, my_bot = self.xfm.px_to_mils(0, 1000)
        assert my_top > my_bot

    def test_snap_to_grid(self):
        assert self.xfm.snap_to_grid(4150.0, 2949.0) == (4200, 2900)
        assert self.xfm.snap_to_grid(4100.0, 3000.0) == (4100, 3000)

    def test_invalid_scale(self):
        with pytest.raises(ValueError):
            CoordTransform(scale_px_per_mil=0.0)


class TestGeometryUtils:
    def test_distance(self):
        p1 = Point(x=0, y=0)
        p2 = Point(x=3, y=4)
        assert distance(p1, p2) == pytest.approx(5.0)

    def test_rotate_point_90(self):
        p = Point(x=1, y=0)
        origin = Point(x=0, y=0)
        r = rotate_point(p, origin, 90)
        assert r.x == pytest.approx(0.0, abs=1e-9)
        assert r.y == pytest.approx(1.0, abs=1e-9)

    def test_rotate_point_180(self):
        p = Point(x=1, y=0)
        origin = Point(x=0, y=0)
        r = rotate_point(p, origin, 180)
        assert r.x == pytest.approx(-1.0, abs=1e-9)
        assert r.y == pytest.approx(0.0, abs=1e-9)

    def test_point_on_segment_true(self):
        p = Point(x=5, y=0)
        p0 = Point(x=0, y=0)
        p1 = Point(x=10, y=0)
        assert point_on_segment(p, p0, p1)

    def test_point_on_segment_false(self):
        p = Point(x=15, y=0)
        p0 = Point(x=0, y=0)
        p1 = Point(x=10, y=0)
        assert not point_on_segment(p, p0, p1)

    def test_closest_point_clamped(self):
        p = Point(x=20, y=0)
        p0 = Point(x=0, y=0)
        p1 = Point(x=10, y=0)
        c = closest_point_on_segment(p, p0, p1)
        assert c.x == pytest.approx(10.0)
        assert c.y == pytest.approx(0.0)

    def test_estimate_scale(self):
        lengths = [120.0] * 5
        scale = estimate_scale_from_passives(lengths, nominal_body_mils=200.0)
        assert scale == pytest.approx(0.6)

    def test_estimate_scale_empty(self):
        with pytest.raises(ValueError):
            estimate_scale_from_passives([])
