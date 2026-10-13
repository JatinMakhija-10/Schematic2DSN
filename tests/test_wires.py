"""
tests/test_wires.py  --  Tests for Stage S4 raster wire detection and splitting.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import Point, WireSegment, WiresFile
from vision.wires import (
    _merge_collinear, _split_at_t_intersections, _estimate_line_thickness
)


def test_wire_segment_properties():
    h_seg = WireSegment(id="W_01", p0=Point(x=10, y=20), p1=Point(x=100, y=20))
    assert h_seg.is_horizontal
    assert not h_seg.is_vertical

    v_seg = WireSegment(id="W_02", p0=Point(x=50, y=10), p1=Point(x=50, y=90))
    assert v_seg.is_vertical
    assert not v_seg.is_horizontal


def test_merge_collinear_horizontal_segments():
    # Two collinear horizontal segments within gap tolerance
    seg1 = WireSegment(id="W_1", p0=Point(x=0, y=100), p1=Point(x=50, y=100))
    seg2 = WireSegment(id="W_2", p0=Point(x=52, y=100), p1=Point(x=120, y=100))
    merged = _merge_collinear([seg1, seg2], lateral_tol=2.0, gap_tol=5.0)

    assert len(merged) == 1
    assert merged[0].p0.x == 0
    assert merged[0].p1.x == 120
    assert merged[0].p0.y == 100


def test_merge_collinear_vertical_segments():
    # Two collinear vertical segments
    seg1 = WireSegment(id="W_1", p0=Point(x=150, y=10), p1=Point(x=150, y=60))
    seg2 = WireSegment(id="W_2", p0=Point(x=150, y=62), p1=Point(x=150, y=110))
    merged = _merge_collinear([seg1, seg2], lateral_tol=2.0, gap_tol=5.0)

    assert len(merged) == 1
    assert merged[0].p0.y == 10
    assert merged[0].p1.y == 110
    assert merged[0].p0.x == 150


def test_split_at_t_intersections():
    # Horizontal line from (0, 50) to (100, 50)
    # Vertical line from (50, 50) to (50, 100) forming a T-junction at (50, 50)
    h_line = WireSegment(id="W_H", p0=Point(x=0, y=50), p1=Point(x=100, y=50))
    v_line = WireSegment(id="W_V", p0=Point(x=50, y=50), p1=Point(x=50, y=100))

    split = _split_at_t_intersections([h_line, v_line])
    # The horizontal line should be split into (0, 50)->(50, 50) and (50, 50)->(100, 50)
    # Plus the vertical segment (50, 50)->(50, 100) = 3 total segments
    assert len(split) == 3

    # Check endpoints meet at (50, 50)
    junction_endpoints = [
        (s.p0.x, s.p0.y) for s in split if (s.p0.x, s.p0.y) == (50.0, 50.0)
    ] + [
        (s.p1.x, s.p1.y) for s in split if (s.p1.x, s.p1.y) == (50.0, 50.0)
    ]
    assert len(junction_endpoints) >= 3


def test_estimate_line_thickness():
    # Synthetic binary image with a 4-pixel thick line
    img = np.zeros((100, 100), dtype=np.uint8)
    img[48:52, :] = 255  # 4 pixels thick
    thickness = _estimate_line_thickness(img)
    assert 2.0 <= thickness <= 6.0
