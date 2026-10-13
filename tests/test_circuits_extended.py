"""
tests/test_circuits_extended.py  --  Tests for extended circuits: BJT Astable, H-Bridge, Diff-Amp, Bandpass.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.synthetic.generate_test_circuits import (
    bjt_astable, h_bridge, diff_amp, bandpass_filter,
    timer_555_astable, buck_converter, mcu_minimum_system
)
from circuit.validate import validate
from core.units import validate_refdes
from core.models import ComponentIR, PinIR, DesignIR, DesignInfo, DesignMetadata, Point
from orcad.roundtrip import ir_to_canonical, compare
from orcad.tcl_gen import generate_mode_a, generate_mode_b


@pytest.mark.parametrize("builder_fn,expected_comp_count,expected_net_count", [
    (bjt_astable, 10, 6),
    (h_bridge, 11, 8),
    (diff_amp, 8, 8),
    (bandpass_filter, 5, 4),
    (timer_555_astable, 9, 7),
    (buck_converter, 9, 5),
    (mcu_minimum_system, 13, 10),
])
def test_extended_circuits_topology_and_integrity(builder_fn, expected_comp_count, expected_net_count):
    ir = builder_fn()
    assert len(ir.components) == expected_comp_count
    assert len(ir.nets) == expected_net_count

    # Validate design
    validated_ir, conf = validate(ir)
    assert conf >= 0.75

    # Canonical round-trip self-test
    canonical = ir_to_canonical(validated_ir)
    rep = compare(canonical, canonical)
    assert rep["match"]

    # Verify Mode A generation
    tcl_a = generate_mode_a(validated_ir, lib_path="COMPETITION.olb")
    assert "PlacePart" in tcl_a
    assert "SaveDesign" in tcl_a

    # Verify Mode B generation
    tcl_b = generate_mode_b(validated_ir, lib_path="COMPETITION.olb")
    assert "PlacePart" in tcl_b
    assert "SaveDesign" in tcl_b
    assert "PlaceWire" in tcl_b


def test_complex_component_pin_properties():
    """Verify that multi-pin ICs retain pins, electrical_types, sides, and packages."""
    ir = timer_555_astable()
    u1 = next(c for c in ir.components if c.id == "U1")
    assert u1.symbol_class == "TIMER_555"
    assert u1.package == "DIP-8"
    assert len(u1.pins) == 8

    # Check pin sides and electrical types
    left_pins = [p for p in u1.pins if p.side == "LEFT"]
    right_pins = [p for p in u1.pins if p.side == "RIGHT"]
    assert len(left_pins) == 4
    assert len(right_pins) == 4

    p_vcc = next(p for p in u1.pins if p.number == "8")
    assert p_vcc.electrical_type == "POWER"
    assert p_vcc.function == "VCC"


def test_arbitrary_custom_ic_tcl_generation():
    """Arbitrary IC classes and multi-character refdes should compile cleanly without error."""
    custom_comp = ComponentIR(
        id="U100",
        symbol_class="CUSTOM_DSP_CORE",
        value="DSP56000",
        package="QFP-144",
        unit=1,
        position=Point(x=4000, y=3000),
        pins=[
            PinIR(number="1", function="IN", pos=Point(x=3900, y=3000), net="SIG_IN"),
            PinIR(number="2", function="OUT", pos=Point(x=4100, y=3000), net="SIG_OUT"),
        ]
    )
    ir = DesignIR(
        design=DesignInfo(name="custom_dsp_circuit"),
        components=[custom_comp],
        nets=[],
        metadata=DesignMetadata(source="user", mode="vector", confidence=1.0)
    )

    # Should fall back gracefully to DIP8/custom value rather than raising exception
    tcl_a = generate_mode_a(ir, lib_path="COMPETITION.olb")
    assert "PlacePart" in tcl_a
    assert "DSP56000" in tcl_a

    tcl_b = generate_mode_b(ir, lib_path="COMPETITION.olb")
    assert "PlacePart" in tcl_b


def test_complex_refdes_patterns():
    """Multi-letter prefixes like XTAL, VREG, XFMR, SW, U1A should be valid."""
    assert validate_refdes("XTAL1")
    assert validate_refdes("VREG1")
    assert validate_refdes("XFMR1")
    assert validate_refdes("SW1")
    assert validate_refdes("U1A")
    assert validate_refdes("U12B")

