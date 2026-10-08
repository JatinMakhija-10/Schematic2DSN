"""
tests/test_roundtrip.py  --  Round-trip tests for the IR exporter.

Tests that:
1. The canonical netlist from the IR matches itself (trivially, for all 5 circuits)
2. ir_to_canonical is deterministic
3. ir_to_canonical ignores net names correctly
4. compare() reports a clean match when netlists are identical

These are the "golden" tests for Day 5 freeze.
"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import DesignIR
from orcad.roundtrip import ir_to_canonical, compare

SYNTHETIC_DIR = Path(__file__).parent.parent / "data" / "synthetic"

CIRCUITS = [
    "voltage_divider",
    "rc_filter",
    "led_driver",
    "inverting_opamp",
    "common_emitter",
]


@pytest.mark.parametrize("name", CIRCUITS)
def test_canonical_self_match(name):
    """IR netlist should match itself in canonical form."""
    design_path = SYNTHETIC_DIR / name / "design.json"
    if not design_path.exists():
        pytest.skip(f"Synthetic data not generated: {design_path}")
    with open(design_path) as f:
        ir = DesignIR.model_validate(json.load(f))
    canonical = ir_to_canonical(ir)
    report = compare(canonical, canonical)
    assert report["match"], f"Self-match failed for {name}: {report}"


@pytest.mark.parametrize("name", CIRCUITS)
def test_canonical_deterministic(name):
    """ir_to_canonical should produce the same result on repeated calls."""
    design_path = SYNTHETIC_DIR / name / "design.json"
    if not design_path.exists():
        pytest.skip(f"Synthetic data not generated: {design_path}")
    with open(design_path) as f:
        ir = DesignIR.model_validate(json.load(f))
    c1 = ir_to_canonical(ir)
    c2 = ir_to_canonical(ir)
    assert c1 == c2


def test_canonical_ignores_net_names():
    """Two IRs with same topology but different net names should match."""
    from data.synthetic.generate_test_circuits import rc_filter
    ir1 = rc_filter()
    ir2 = rc_filter()
    # Rename one net
    for net in ir2.nets:
        if net.name == "OUT":
            net.name = "RENAMED_OUT"
            net.auto_named = True
    c1 = ir_to_canonical(ir1)
    c2 = ir_to_canonical(ir2)
    assert c1 == c2, "Topology should match regardless of net name"


def test_mismatch_detected():
    """compare() should detect when a net is missing."""
    from data.synthetic.generate_test_circuits import voltage_divider
    ir1 = voltage_divider()
    ir2 = voltage_divider()
    # Remove one pin from one net in ir2
    ir2.nets[0].pins = ir2.nets[0].pins[:1]
    c1 = ir_to_canonical(ir1)
    c2 = ir_to_canonical(ir2)
    report = compare(c1, c2)
    assert not report["match"]


def test_tcl_roundtrip_demo():
    """Demo IR -> Tcl generation -> no exceptions."""
    from orcad.tcl_gen import make_demo_ir, generate_mode_a
    ir = make_demo_ir()
    script = generate_mode_a(ir, lib_path="COMPETITION.olb")
    assert "PlacePart" in script
    assert "SaveDesign" in script
    assert "R1" in script


@pytest.mark.parametrize("name", CIRCUITS)
def test_tcl_gen_on_synthetic(name, tmp_path):
    """tcl_gen should generate valid Tcl for all synthetic circuits."""
    from orcad.tcl_gen import generate_mode_a
    design_path = SYNTHETIC_DIR / name / "design.json"
    if not design_path.exists():
        pytest.skip(f"Synthetic data not generated: {design_path}")
    with open(design_path) as f:
        ir = DesignIR.model_validate(json.load(f))
    out = tmp_path / f"{name}.tcl"
    script = generate_mode_a(ir, lib_path="COMPETITION.olb", output_path=str(out))
    assert out.exists()
    assert "PlacePart" in script
    assert "SaveDesign" in script
    # Every component refdes should appear
    for comp in ir.components:
        assert comp.id in script, f"Refdes {comp.id} not in Tcl output"
