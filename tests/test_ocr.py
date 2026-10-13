"""
tests/test_ocr.py  --  Tests for Stage S2 OCR post-processing and text normalization.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import TextItem, TextsFile, BBox
from core.units import normalize_value, fix_refdes, REFDES_PATTERN
from vision.ocr import _iou, _merge_by_confidence, _postprocess


def test_iou_identical_boxes():
    b1 = BBox(x0=10, y0=10, x1=50, y1=50)
    b2 = BBox(x0=10, y0=10, x1=50, y1=50)
    assert abs(_iou(b1, b2) - 1.0) < 1e-4


def test_iou_disjoint_boxes():
    b1 = BBox(x0=0, y0=0, x1=10, y1=10)
    b2 = BBox(x0=20, y0=20, x1=30, y1=30)
    assert _iou(b1, b2) == 0.0


def test_iou_partial_overlap():
    b1 = BBox(x0=0, y0=0, x1=20, y1=20)   # area 400
    b2 = BBox(x0=10, y0=0, x1=30, y1=20)  # area 400, intersection area 200
    # union = 400 + 400 - 200 = 600 -> iou = 200/600 = 1/3
    assert abs(_iou(b1, b2) - (1.0 / 3.0)) < 1e-4


def test_merge_by_confidence_keeps_higher():
    item_low = TextItem(
        text="R1",
        bbox=BBox(x0=10, y0=10, x1=30, y1=20),
        angle=0,
        conf=0.6,
        source="ocr"
    )
    item_high = TextItem(
        text="R1",
        bbox=BBox(x0=12, y0=10, x1=32, y1=20),
        angle=90,
        conf=0.95,
        source="ocr"
    )
    merged = _merge_by_confidence([item_low], [item_high], iou_threshold=0.3)
    assert len(merged) == 1
    assert merged[0].conf == 0.95


def test_merge_by_confidence_keeps_disjoint():
    item1 = TextItem(text="R1", bbox=BBox(x0=0, y0=0, x1=20, y1=20), conf=0.8)
    item2 = TextItem(text="C1", bbox=BBox(x0=100, y0=100, x1=120, y1=120), conf=0.85)
    merged = _merge_by_confidence([item1], [item2], iou_threshold=0.3)
    assert len(merged) == 2


def test_postprocess_normalizes_values_and_refdes():
    items = [
        TextItem(text="4k7", bbox=BBox(x0=0, y0=0, x1=10, y1=10), conf=0.9),
        TextItem(text="10K", bbox=BBox(x0=20, y0=0, x1=30, y1=10), conf=0.9),
        TextItem(text=".1uF", bbox=BBox(x0=40, y0=0, x1=50, y1=10), conf=0.9),
        TextItem(text="100R", bbox=BBox(x0=60, y0=0, x1=70, y1=10), conf=0.9),
        TextItem(text="RI", bbox=BBox(x0=80, y0=0, x1=90, y1=10), conf=0.9),  # OCR typo: RI -> R1
    ]
    res = _postprocess(items)
    texts = [item.text for item in res]
    assert texts[0] == "4.7k"
    assert texts[1] == "10k"
    assert texts[2] == "0.1uF"
    assert texts[3] == "100ohm"
    assert texts[4] == "R1"


def test_refdes_pattern_matching():
    valid = ["R1", "R12", "C100", "Q1", "U1A", "D2", "LED1", "J1"]
    for v in valid:
        assert REFDES_PATTERN.match(v) is not None, f"Expected {v} to be valid RefDes"

    invalid = ["10k", "100nF", "GND", "++", "123", ""]
    for inv in invalid:
        assert REFDES_PATTERN.match(inv) is None, f"Expected {inv} to be invalid RefDes"
