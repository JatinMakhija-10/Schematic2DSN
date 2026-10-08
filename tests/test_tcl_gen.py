"""
tests/test_tcl_gen.py  --  Tests for the Tcl script generator.

Run with: pytest tests/test_tcl_gen.py -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
import pytest
from orcad.tcl_gen import make_demo_ir, generate_mode_a, _snap


class TestSnap:
    def test_snap_round_up(self):
        assert _snap(4150, 100) == 4200

    def test_snap_round_down(self):
        assert _snap(4049, 100) == 4000

    def test_already_on_grid(self):
        assert _snap(4200, 100) == 4200


class TestDemoIR:
    def test_demo_ir_valid(self):
        ir = make_demo_ir()
        assert len(ir.components) == 4
        assert len(ir.nets) == 3

    def test_demo_ir_schema(self):
        ir = make_demo_ir()
        assert ir.schema_version == '1.0'

    def test_demo_r1_pins(self):
        ir = make_demo_ir()
        r1 = next(c for c in ir.components if c.id == 'R1')
        assert len(r1.pins) == 2
        nets = {p.net for p in r1.pins}
        assert 'VCC' in nets
        assert 'NET_001' in nets


class TestGenerateModeA:
    def test_generates_string(self, tmp_path):
        ir = make_demo_ir()
        out = tmp_path / 'test.tcl'
        script = generate_mode_a(ir, lib_path='COMPETITION.olb', output_path=str(out))
        assert isinstance(script, str)
        assert len(script) > 0
        assert out.exists()

    def test_contains_place_part(self):
        ir = make_demo_ir()
        script = generate_mode_a(ir, lib_path='COMPETITION.olb')
        assert 'PlacePart' in script

    def test_contains_refdes(self):
        ir = make_demo_ir()
        script = generate_mode_a(ir, lib_path='COMPETITION.olb')
        assert 'R1' in script
        assert 'C1' in script

    def test_contains_net_alias(self):
        ir = make_demo_ir()
        script = generate_mode_a(ir, lib_path='COMPETITION.olb')
        assert 'PlaceNetAlias' in script
        assert 'VCC' in script
        assert 'GND' in script

    def test_net_aliases_on_grid(self):
        ir = make_demo_ir()
        script = generate_mode_a(ir, lib_path='COMPETITION.olb')
        for m in re.finditer(r'PlaceNetAlias (\d+) (\d+)', script):
            x, y = int(m.group(1)), int(m.group(2))
            assert x % 100 == 0
            assert y % 100 == 0
