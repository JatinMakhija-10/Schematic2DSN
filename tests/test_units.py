"""
tests/test_units.py  --  Tests for value normalization and refdes fixing.

Run with: pytest tests/test_units.py -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from core.units import normalize_value, fix_refdes


class TestNormalizeValue:
    def test_leading_dot(self):
        assert normalize_value('.1uF') == '0.1uF'

    def test_uppercase_k(self):
        assert normalize_value('10K') == '10k'

    def test_4k7_form(self):
        result = normalize_value('4k7')
        assert '4' in result and '7' in result and 'k' in result

    def test_mu_variants(self):
        assert 'u' in normalize_value('1\u00b5F')
        assert 'u' in normalize_value('1\u03bcF')

    def test_passthrough_clean(self):
        assert normalize_value('10k') == '10k'
        assert normalize_value('100nF') == '100nF'


class TestFixRefdes:
    def test_valid_refdes(self):
        assert fix_refdes('R1') == 'R1'
        assert fix_refdes('C12') == 'C12'
        assert fix_refdes('U3A') == 'U3A'

    def test_class_prefix_resistor(self):
        assert fix_refdes('R1', 'RESISTOR') == 'R1'

    def test_class_prefix_mismatch_kept(self):
        result = fix_refdes('C1', 'RESISTOR')
        assert result == 'C1'
