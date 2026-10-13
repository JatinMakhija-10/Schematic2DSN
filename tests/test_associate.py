"""
tests/test_associate.py  --  Tests for Stage S8 RefDes and Value association (Hungarian algorithm).
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import BBox, SymbolItem, SymbolsFile, TextItem, TextsFile
from circuit.associate import associate, _cost


def test_cost_calculation():
    sym = SymbolItem(
        id="SYM_01", symbol_class="RESISTOR",
        bbox=BBox(x0=100, y0=100, x1=200, y1=140),  # cx=150, cy=120
        conf=0.9
    )
    # Valid resistor text near symbol
    txt_valid = TextItem(text="R1", bbox=BBox(x0=150, y0=150, x1=170, y1=160), conf=0.9)
    # Text with wrong prefix (C1 near resistor)
    txt_wrong_prefix = TextItem(text="C1", bbox=BBox(x0=150, y0=150, x1=170, y1=160), conf=0.9)

    cost_valid = _cost(sym, txt_valid)
    cost_wrong = _cost(sym, txt_wrong_prefix)

    # Wrong prefix should incur heavy penalty
    assert cost_wrong > cost_valid + 400.0


def test_associate_hungarian_matching():
    # 2 resistors, 2 refdes texts, 2 value texts
    r1_sym = SymbolItem(
        id="SYM_01", symbol_class="RESISTOR",
        bbox=BBox(x0=100, y0=100, x1=200, y1=140), conf=0.95
    )
    r2_sym = SymbolItem(
        id="SYM_02", symbol_class="RESISTOR",
        bbox=BBox(x0=400, y0=100, x1=500, y1=140), conf=0.95
    )
    symbols = SymbolsFile(items=[r1_sym, r2_sym])

    t_r1 = TextItem(text="R1", bbox=BBox(x0=140, y0=150, x1=160, y1=165), conf=0.9)
    t_v1 = TextItem(text="10k", bbox=BBox(x0=140, y0=70, x1=160, y1=85), conf=0.9)

    t_r2 = TextItem(text="R2", bbox=BBox(x0=440, y0=150, x1=460, y1=165), conf=0.9)
    t_v2 = TextItem(text="4k7", bbox=BBox(x0=440, y0=70, x1=460, y1=85), conf=0.9)

    texts = TextsFile(items=[t_r1, t_v1, t_r2, t_v2])

    comps, warnings = associate(symbols, texts)
    assert len(comps) == 2
    r1_comp = [c for c in comps if c.id == "R1"][0]
    r2_comp = [c for c in comps if c.id == "R2"][0]

    assert r1_comp.value == "10k"
    assert r2_comp.value == "4.7k"  # normalized 4k7 -> 4.7k
    assert len(warnings) == 0


def test_associate_unmatched_symbol_gets_auto_refdes():
    # A capacitor with no refdes text nearby
    c_sym = SymbolItem(
        id="SYM_C1", symbol_class="CAPACITOR",
        bbox=BBox(x0=200, y0=200, x1=250, y1=250), conf=0.8
    )
    symbols = SymbolsFile(items=[c_sym])
    texts = TextsFile(items=[])

    comps, warnings = associate(symbols, texts)
    assert len(comps) == 1
    assert comps[0].id == "C_AUTO1"
    assert any(w.code == "UNMATCHED_SYMBOL" for w in warnings)
