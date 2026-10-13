"""
tests/test_symbols_yolo.py  --  Tests for Stage S3 YOLO detector and fallback mode.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vision.symbols_yolo import detect_symbols_yolo, CLASSES
from core.models import SymbolsFile


def test_yolo_fallback_when_weights_missing(tmp_path):
    # Pass a path to non-existent weights
    non_existent_weights = str(tmp_path / "missing_yolo.pt")
    dummy_img = str(tmp_path / "dummy.png")
    Path(dummy_img).write_bytes(b"")

    symbols = detect_symbols_yolo(dummy_img, weights_path=non_existent_weights)
    assert isinstance(symbols, SymbolsFile)
    # When weights don't exist, must gracefully return empty so OpenCV heuristics handle it
    assert len(symbols.items) == 0


def test_yolo_class_taxonomy_completeness():
    expected_classes = [
        "RESISTOR", "CAPACITOR", "INDUCTOR", "DIODE", "LED",
        "GROUND", "VCC", "OPAMP", "NPN", "PNP", "NMOS", "PMOS", "CONNECTOR"
    ]
    for c in expected_classes:
        assert c in CLASSES
    assert len(CLASSES) == 13
