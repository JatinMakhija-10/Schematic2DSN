"""
tests/test_confidence.py  --  Tests for formalized confidence score calculation.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    DesignIR, DesignInfo, DesignMetadata, ComponentIR, PinIR, NetIR, WarningIR, Point
)
from circuit.confidence import compute_design_confidence


def test_confidence_empty_design():
    ir = DesignIR(
        design=DesignInfo(name="empty"),
        components=[],
        nets=[],
        warnings=[]
    )
    assert compute_design_confidence(ir) == 0.0


def test_confidence_perfect_design():
    # 100% connected, high confidence, 0 warnings
    comp = ComponentIR(
        id="R1", symbol_class="RESISTOR", value="10k",
        position=Point(x=100, y=100), confidence=1.0,
        pins=[
            PinIR(number="1", function="A", pos=Point(x=50, y=100), net="VCC"),
            PinIR(number="2", function="B", pos=Point(x=150, y=100), net="GND"),
        ]
    )
    vcc = ComponentIR(
        id="VCC1", symbol_class="VCC", value="",
        position=Point(x=50, y=100), confidence=1.0,
        pins=[PinIR(number="1", function="PWR", pos=Point(x=50, y=100), net="VCC")]
    )
    gnd = ComponentIR(
        id="GND1", symbol_class="GROUND", value="",
        position=Point(x=150, y=100), confidence=1.0,
        pins=[PinIR(number="1", function="PWR", pos=Point(x=150, y=100), net="GND")]
    )
    nets = [
        NetIR(name="VCC", auto_named=False, pins=[["R1", "1"], ["VCC1", "1"]]),
        NetIR(name="GND", auto_named=False, pins=[["R1", "2"], ["GND1", "1"]]),
    ]
    ir = DesignIR(
        design=DesignInfo(name="perfect"),
        components=[comp, vcc, gnd],
        nets=nets,
        warnings=[],
        metadata=DesignMetadata(source="test", mode="vector", confidence=1.0, ocr_confidence=1.0)
    )

    conf = compute_design_confidence(ir)
    assert abs(conf - 1.0) < 1e-3


def test_confidence_penalized_by_critical_warnings():
    comp = ComponentIR(
        id="R1", symbol_class="RESISTOR", value="10k",
        position=Point(x=100, y=100), confidence=0.8,
        pins=[
            PinIR(number="1", function="A", pos=Point(x=50, y=100), net=None),
            PinIR(number="2", function="B", pos=Point(x=150, y=100), net=None),
        ]
    )
    ir_clean = DesignIR(
        design=DesignInfo(name="clean"),
        components=[comp],
        nets=[],
        warnings=[],
        metadata=DesignMetadata(source="test", mode="vector", confidence=0.0, ocr_confidence=0.8)
    )

    ir_warn = DesignIR(
        design=DesignInfo(name="warn"),
        components=[comp],
        nets=[],
        warnings=[
            WarningIR(code="UNCONNECTED_PIN", detail="Pin 1 unconnected"),
            WarningIR(code="UNCONNECTED_PIN", detail="Pin 2 unconnected"),
            WarningIR(code="DUPLICATE_REFDES", detail="Duplicate R1"),
        ],
        metadata=DesignMetadata(source="test", mode="vector", confidence=0.0, ocr_confidence=0.8)
    )

    conf_clean = compute_design_confidence(ir_clean)
    conf_warn = compute_design_confidence(ir_warn)
    assert conf_warn < conf_clean
