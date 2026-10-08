"""
tests/test_validate.py  --  Tests for circuit/validate.py
"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    DesignIR, DesignInfo, ComponentIR, PinIR, NetIR, WarningIR, DesignMetadata, Point
)
from circuit.validate import validate


def _make_simple_ir() -> DesignIR:
    """R1 between VCC and GND."""
    r1 = ComponentIR(
        id="R1", symbol_class="RESISTOR", value="10k",
        unit=1, position=Point(x=4000, y=3000),
        rotation=0, mirror=False, confidence=0.9,
        pins=[
            PinIR(number="1", function="A", pos=Point(x=3900, y=3000), net="VCC"),
            PinIR(number="2", function="B", pos=Point(x=4100, y=3000), net="GND"),
        ]
    )
    vcc = ComponentIR(
        id="VCC1", symbol_class="VCC", value="",
        unit=1, position=Point(x=3800, y=3200),
        rotation=0, mirror=False, confidence=1.0,
        pins=[PinIR(number="1", function="PWR", pos=Point(x=3800, y=3100), net="VCC")]
    )
    gnd = ComponentIR(
        id="GND1", symbol_class="GROUND", value="",
        unit=1, position=Point(x=4200, y=2800),
        rotation=0, mirror=False, confidence=1.0,
        pins=[PinIR(number="1", function="PWR", pos=Point(x=4200, y=2900), net="GND")]
    )
    nets = [
        NetIR(name="VCC", auto_named=False, pins=[["R1", "1"], ["VCC1", "1"]]),
        NetIR(name="GND", auto_named=False, pins=[["R1", "2"], ["GND1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="test"),
        components=[r1, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="test", mode="vector",
                                confidence=0.0, ocr_confidence=1.0)
    )


class TestValidate:
    def test_clean_ir_no_critical_warnings(self):
        ir = _make_simple_ir()
        validated, conf = validate(ir)
        # Should have no UNCONNECTED_PIN, DUPLICATE_REFDES, etc.
        critical = [w for w in validated.warnings if w.code in {
            "UNCONNECTED_PIN", "DUPLICATE_REFDES", "PIN_ON_TWO_NETS"
        }]
        assert len(critical) == 0

    def test_confidence_range(self):
        ir = _make_simple_ir()
        _, conf = validate(ir)
        assert 0.0 <= conf <= 1.0

    def test_duplicate_refdes_flagged(self):
        ir = _make_simple_ir()
        # Duplicate R1
        ir.components.append(
            ComponentIR(id="R1", symbol_class="RESISTOR", value="1k",
                        unit=1, position=Point(x=5000, y=3000),
                        rotation=0, mirror=False, confidence=0.8,
                        pins=[
                            PinIR(number="1", function="A", pos=Point(x=4900, y=3000), net="VCC"),
                            PinIR(number="2", function="B", pos=Point(x=5100, y=3000), net="GND"),
                        ])
        )
        validated, _ = validate(ir)
        codes = [w.code for w in validated.warnings]
        assert "DUPLICATE_REFDES" in codes

    def test_unconnected_pin_flagged(self):
        ir = _make_simple_ir()
        # Add a component with no net on pin 2
        ir.components.append(
            ComponentIR(id="R3", symbol_class="RESISTOR", value="1k",
                        unit=1, position=Point(x=5000, y=3000),
                        rotation=0, mirror=False, confidence=0.8,
                        pins=[
                            PinIR(number="1", function="A", pos=Point(x=4900, y=3000), net="VCC"),
                            PinIR(number="2", function="B", pos=Point(x=5100, y=3000), net=None),
                        ])
        )
        validated, _ = validate(ir)
        codes = [w.code for w in validated.warnings]
        assert "UNCONNECTED_PIN" in codes

    def test_confidence_decreases_with_warnings(self):
        ir_clean = _make_simple_ir()
        ir_warn = _make_simple_ir()
        # Add multiple unconnected pins
        for i in range(5):
            ir_warn.components.append(
                ComponentIR(id=f"R{10+i}", symbol_class="RESISTOR", value="1k",
                            unit=1, position=Point(x=5000+i*200, y=3000),
                            rotation=0, mirror=False, confidence=0.5,
                            pins=[
                                PinIR(number="1", function="A",
                                      pos=Point(x=4900+i*200, y=3000), net=None),
                                PinIR(number="2", function="B",
                                      pos=Point(x=5100+i*200, y=3000), net=None),
                            ])
            )
        _, conf_clean = validate(ir_clean)
        _, conf_warn = validate(ir_warn)
        assert conf_warn < conf_clean
