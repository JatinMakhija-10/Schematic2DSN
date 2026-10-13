"""
tests/test_junctions.py  --  Tests for Stage S5 junction dots and crossing topology.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import Point, WireSegment, WiresFile, JunctionItem, JunctionsFile
from vision.junctions import detect_junction_dots, classify_crossings


def test_detect_junction_dots_from_image(tmp_path):
    # Create white image with black background (or vice versa for binarization)
    img = np.zeros((200, 200), dtype=np.uint8)
    # Draw a thin line (thickness 2)
    cv2.line(img, (20, 100), (180, 100), 255, 2)
    # Draw a circular solder dot (radius 7, diameter 14)
    cv2.circle(img, (100, 100), 7, 255, -1)

    # Invert to match typical white paper background
    paper = 255 - img
    img_path = tmp_path / "dots_test.png"
    cv2.imwrite(str(img_path), paper)

    dots = detect_junction_dots(str(img_path))
    # Should detect the dot at ~(100, 100) and ignore the thin line
    assert len(dots) >= 1
    dot = dots[0]
    assert abs(dot.pos.x - 100) < 5
    assert abs(dot.pos.y - 100) < 5
    assert dot.radius >= 4.0


def test_classify_crossings_four_way_with_dot():
    # 4 segments meeting at (100, 100)
    segs = [
        WireSegment(id="W1", p0=Point(x=0, y=100), p1=Point(x=100, y=100)),
        WireSegment(id="W2", p0=Point(x=100, y=100), p1=Point(x=200, y=100)),
        WireSegment(id="W3", p0=Point(x=100, y=0), p1=Point(x=100, y=100)),
        WireSegment(id="W4", p0=Point(x=100, y=100), p1=Point(x=100, y=200)),
    ]
    wires = WiresFile(segments=segs, endpoints=[s.p0 for s in segs] + [s.p1 for s in segs])
    dots = [JunctionItem(pos=Point(x=100, y=100), radius=6.0)]

    connected, ambiguous, warnings = classify_crossings(wires, dots, tol=6.0)
    # With dot, should be classified as connected
    assert any(abs(p.x - 100) < 1 and abs(p.y - 100) < 1 for p in connected)
    assert len(ambiguous) == 0
    assert len(warnings) == 0


def test_classify_crossings_four_way_without_dot_emits_ambiguous():
    # 4 segments meeting at (100, 100) WITHOUT a solder dot
    segs = [
        WireSegment(id="W1", p0=Point(x=0, y=100), p1=Point(x=100, y=100)),
        WireSegment(id="W2", p0=Point(x=100, y=100), p1=Point(x=200, y=100)),
        WireSegment(id="W3", p0=Point(x=100, y=0), p1=Point(x=100, y=100)),
        WireSegment(id="W4", p0=Point(x=100, y=100), p1=Point(x=100, y=200)),
    ]
    wires = WiresFile(segments=segs, endpoints=[s.p0 for s in segs] + [s.p1 for s in segs])
    dots = []  # No dot!

    connected, ambiguous, warnings = classify_crossings(wires, dots, tol=6.0)
    # Should flag ambiguous crossing
    assert any(abs(p.x - 100) < 1 and abs(p.y - 100) < 1 for p in ambiguous)
    assert len(warnings) >= 1
    assert warnings[0]["code"] == "AMBIGUOUS_JUNCTION"


def test_classify_crossings_t_junction_always_connected():
    # 3 segments meeting at (50, 50) - T-junction
    segs = [
        WireSegment(id="W1", p0=Point(x=0, y=50), p1=Point(x=50, y=50)),
        WireSegment(id="W2", p0=Point(x=50, y=50), p1=Point(x=100, y=50)),
        WireSegment(id="W3", p0=Point(x=50, y=50), p1=Point(x=50, y=100)),
    ]
    wires = WiresFile(segments=segs, endpoints=[s.p0 for s in segs] + [s.p1 for s in segs])
    dots = []  # Even without dot, T-junction is always connected

    connected, ambiguous, warnings = classify_crossings(wires, dots, tol=6.0)
    assert any(abs(p.x - 50) < 1 and abs(p.y - 50) < 1 for p in connected)
    assert len(ambiguous) == 0
