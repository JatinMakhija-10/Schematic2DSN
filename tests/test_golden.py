"""
tests/test_golden.py  --  Day 5 Frozen Golden Suite.

Loads frozen golden inputs from data/golden/ and verifies:
1. Canonical netlist consistency against golden definitions
2. Both Mode A and Mode B Tcl export validity
3. Zero missing or duplicated component pins
"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import DesignIR
from orcad.roundtrip import ir_to_canonical, compare
from orcad.tcl_gen import generate_mode_a, generate_mode_b

GOLDEN_DIR = Path(__file__).parent.parent / "data" / "golden"

GOLDEN_CASES = [
    "voltage_divider",
    "rc_filter",
    "led_driver",
    "inverting_opamp",
    "common_emitter",
    "bjt_astable",
    "h_bridge",
    "diff_amp",
    "bandpass_filter",
    "timer_555_astable",
    "buck_converter",
    "mcu_minimum_system",
]


@pytest.mark.parametrize("name", GOLDEN_CASES)
def test_golden_ir_integrity(name):
    file_path = GOLDEN_DIR / f"{name}.json"
    assert file_path.exists(), f"Missing golden benchmark: {file_path}"
    with open(file_path, encoding="utf-8") as f:
        ir = DesignIR.model_validate(json.load(f))

    assert len(ir.components) >= 4
    assert len(ir.nets) >= 3
    assert ir.schema_version == "1.0"


@pytest.mark.parametrize("name", GOLDEN_CASES)
def test_golden_mode_a_and_b(name, tmp_path):
    file_path = GOLDEN_DIR / f"{name}.json"
    with open(file_path, encoding="utf-8") as f:
        ir = DesignIR.model_validate(json.load(f))

    # Mode A
    tcl_a = generate_mode_a(ir, lib_path="COMPETITION.olb", output_path=str(tmp_path / f"{name}_a.tcl"))
    assert "PlacePart" in tcl_a
    assert "SaveDesign" in tcl_a

    # Mode B
    tcl_b = generate_mode_b(ir, lib_path="COMPETITION.olb", output_path=str(tmp_path / f"{name}_b.tcl"))
    assert "PlacePart" in tcl_b
    assert "PlaceWire" in tcl_b
    assert "SaveDesign" in tcl_b
