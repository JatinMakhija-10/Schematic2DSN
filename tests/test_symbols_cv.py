"""
tests/test_symbols_cv.py  --  Tests for Stage S3 OpenCV symbol detection heuristics.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import BBox, SymbolItem, SymbolsFile, TextItem, TextsFile
from vision.symbols_cv import (
    _circularity, _bbox_iou, _deduplicate, _mask_text_regions, _CLASS_COLORS
)


def test_circularity_perfect_circle():
    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(img, (50, 50), 20, 255, -1)
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    assert len(contours) > 0
    circ = _circularity(contours[0])
    # A discrete digital circle has circularity close to 0.85-1.0
    assert 0.75 <= circ <= 1.05


def test_circularity_thin_line():
    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.line(img, (10, 50), (90, 50), 255, 1)
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circ = _circularity(contours[0])
    assert circ < 0.3


def test_bbox_iou():
    a = BBox(x0=0, y0=0, x1=50, y1=50)
    b = BBox(x0=0, y0=0, x1=50, y1=50)
    assert abs(_bbox_iou(a, b) - 1.0) < 1e-4

    c = BBox(x0=100, y0=100, x1=150, y1=150)
    assert _bbox_iou(a, c) == 0.0


def test_deduplicate_keeps_highest_confidence():
    sym1 = SymbolItem(
        id="SYM_01", symbol_class="RESISTOR",
        bbox=BBox(x0=10, y0=10, x1=60, y1=30),
        conf=0.7, source="cv"
    )
    sym2 = SymbolItem(
        id="SYM_02", symbol_class="RESISTOR",
        bbox=BBox(x0=12, y0=10, x1=62, y1=30),
        conf=0.92, source="cv"
    )
    dedup = _deduplicate([sym1, sym2], iou_threshold=0.5)
    assert len(dedup) == 1
    assert dedup[0].id == "SYM_02"
    assert dedup[0].conf == 0.92


def test_mask_text_regions():
    binary = np.ones((100, 100), dtype=np.uint8) * 255
    text = TextItem(text="R1", bbox=BBox(x0=20, y0=20, x1=40, y1=40), conf=0.9)
    texts = TextsFile(items=[text])

    masked = _mask_text_regions(binary, texts, dilate_px=2)
    # Area inside the text bbox should be zeroed out
    assert np.all(masked[22:38, 22:38] == 0)
    # Outside should still be 255
    assert masked[5, 5] == 255


def test_class_colors_palette_complete():
    expected_classes = [
        "RESISTOR", "CAPACITOR", "INDUCTOR", "DIODE", "LED",
        "GROUND", "VCC", "OPAMP", "NPN", "PNP", "NMOS", "PMOS", "CONNECTOR"
    ]
    for cls_name in expected_classes:
        assert cls_name in _CLASS_COLORS
        color = _CLASS_COLORS[cls_name]
        assert len(color) == 3
        b, g, r = color
        # Disallow pure green (G high, B and R low)
        assert not (g > 150 and b < 50 and r < 50), f"{cls_name} color {color} is green"
        # Disallow pure purple/magenta (B and R high, G low)
        assert not (b > 120 and r > 120 and g < 50), f"{cls_name} color {color} is purple"
