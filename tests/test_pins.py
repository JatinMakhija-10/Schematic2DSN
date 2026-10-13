"""
tests/test_pins.py  --  Tests for Stage S6 Pin calculation and snapping.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import BBox, Point, SymbolItem, WireSegment, WiresFile
from vision.pins import compute_pin_positions, snap_pins_to_wires


def test_compute_pin_positions_resistor_horizontal():
    # Horizontal resistor centered at (500, 300) with scale 1.0 (1 px per mil)
    sym = SymbolItem(
        id="SYM_01", symbol_class="RESISTOR",
        bbox=BBox(x0=400, y0=280, x1=600, y1=320),  # cx=500, cy=300
        rotation=0, mirror=False, conf=1.0, source="cv"
    )
    pins = compute_pin_positions(sym, scale_px_per_mil=1.0)
    assert len(pins) == 2
    # Pin 1 at dx=-100 -> x=400, y=300
    # Pin 2 at dx=100 -> x=600, y=300
    p1 = [p for p in pins if p[0] == "1"][0]
    p2 = [p for p in pins if p[0] == "2"][0]
    assert p1[2].x == 400
    assert p1[2].y == 300
    assert p2[2].x == 600
    assert p2[2].y == 300


def test_compute_pin_positions_resistor_vertical():
    # Vertical resistor rot=90
    sym = SymbolItem(
        id="SYM_01", symbol_class="RESISTOR",
        bbox=BBox(x0=480, y0=200, x1=520, y1=400),  # cx=500, cy=300
        rotation=90, mirror=False, conf=1.0, source="cv"
    )
    pins = compute_pin_positions(sym, scale_px_per_mil=1.0)
    assert len(pins) == 2
    p1 = [p for p in pins if p[0] == "1"][0]
    p2 = [p for p in pins if p[0] == "2"][0]
    # In rot90: dx=0, dy=100 for pin 1, so py = 300 - 100 = 200
    assert p1[2].x == 500
    assert p1[2].y == 200
    assert p2[2].x == 500
    assert p2[2].y == 400


def test_compute_pin_positions_opamp_5pins():
    sym = SymbolItem(
        id="SYM_U1", symbol_class="OPAMP",
        bbox=BBox(x0=300, y0=200, x1=500, y1=400),  # cx=400, cy=300
        rotation=0, mirror=False, conf=1.0, source="cv"
    )
    pins = compute_pin_positions(sym, scale_px_per_mil=1.0)
    assert len(pins) == 5
    funcs = {p[1] for p in pins}
    assert funcs == {"IN_MINUS", "IN_PLUS", "VS_PLUS", "VS_MINUS", "OUT"}


def test_snap_pins_to_wires_within_tolerance():
    pin_points = [
        ("1", "A", Point(x=402, y=301)),  # within 6 px of wire endpoint (400, 300)
        ("2", "B", Point(x=598, y=299)),  # within 6 px of wire endpoint (600, 300)
    ]
    wires = WiresFile(
        segments=[],
        endpoints=[Point(x=400, y=300), Point(x=600, y=300)]
    )
    snapped = snap_pins_to_wires(pin_points, wires, tolerance_px=6.0)
    assert len(snapped) == 2
    assert (snapped[0].pos.x, snapped[0].pos.y) == (400.0, 300.0)
    assert (snapped[1].pos.x, snapped[1].pos.y) == (600.0, 300.0)


def test_snap_pins_to_wires_out_of_tolerance():
    pin_points = [
        ("1", "A", Point(x=450, y=300)),  # far from (400, 300)
    ]
    wires = WiresFile(
        segments=[],
        endpoints=[Point(x=400, y=300)]
    )
    snapped = snap_pins_to_wires(pin_points, wires, tolerance_px=6.0)
    assert len(snapped) == 1
    # Remains unsnapped at expected position
    assert (snapped[0].pos.x, snapped[0].pos.y) == (450.0, 300.0)
    assert snapped[0].net is None
