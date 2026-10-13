"""
tests/test_vector_extract.py  --  Tests for Stage S2/S4 vector extraction functions.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import Point, BBox, WireSegment
from vision.vector_extract import (
    _is_horizontal, _is_vertical, _snap_orthogonal, _merge_collinear
)


def test_is_horizontal():
    # Exactly horizontal
    assert _is_horizontal((0.0, 10.0), (100.0, 10.0))
    # Nearly horizontal (within 5 deg)
    assert _is_horizontal((0.0, 10.0), (100.0, 12.0), tol_deg=5.0)
    # Strictly vertical
    assert not _is_horizontal((10.0, 0.0), (10.0, 100.0))
    # Diagonal 45 deg
    assert not _is_horizontal((0.0, 0.0), (100.0, 100.0))


def test_is_vertical():
    # Exactly vertical
    assert _is_vertical((10.0, 0.0), (10.0, 100.0))
    # Nearly vertical
    assert _is_vertical((10.0, 0.0), (12.0, 100.0), tol_deg=5.0)
    # Strictly horizontal
    assert not _is_vertical((0.0, 10.0), (100.0, 10.0))


def test_snap_orthogonal():
    # Nearly horizontal snapped to constant y
    p0, p1 = _snap_orthogonal((0.0, 10.0), (100.0, 12.0))
    assert p0[1] == 11.0
    assert p1[1] == 11.0

    # Nearly vertical snapped to constant x
    p0, p1 = _snap_orthogonal((10.0, 0.0), (12.0, 100.0))
    assert p0[0] == 11.0
    assert p1[0] == 11.0


def test_merge_collinear_horizontal():
    # Two touching segments along y=50
    seg1 = WireSegment(id="W_01", p0=Point(x=10, y=50), p1=Point(x=50, y=50))
    seg2 = WireSegment(id="W_02", p0=Point(x=50, y=50), p1=Point(x=100, y=50))
    merged = _merge_collinear([seg1, seg2], lateral_tol=2.0, gap_tol=3.0)
    assert len(merged) == 1
    assert merged[0].p0.x == 10
    assert merged[0].p1.x == 100
    assert merged[0].p0.y == 50


def test_merge_collinear_vertical():
    # Two overlapping segments along x=80
    seg1 = WireSegment(id="W_01", p0=Point(x=80, y=20), p1=Point(x=80, y=60))
    seg2 = WireSegment(id="W_02", p0=Point(x=80, y=50), p1=Point(x=80, y=120))
    merged = _merge_collinear([seg1, seg2], lateral_tol=2.0, gap_tol=3.0)
    assert len(merged) == 1
    assert merged[0].p0.y == 20
    assert merged[0].p1.y == 120
    assert merged[0].p0.x == 80


def test_merge_keeps_separated_segments():
    # Two separated segments with gap > 3.0
    seg1 = WireSegment(id="W_01", p0=Point(x=10, y=50), p1=Point(x=40, y=50))
    seg2 = WireSegment(id="W_02", p0=Point(x=60, y=50), p1=Point(x=100, y=50))
    merged = _merge_collinear([seg1, seg2], lateral_tol=2.0, gap_tol=3.0)
    assert len(merged) == 2
