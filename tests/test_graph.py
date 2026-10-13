"""
tests/test_graph.py  --  Tests for Stage S7 Net Graph extraction and Union-Find.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    Point, WireSegment, WiresFile, JunctionItem, JunctionsFile,
    TextItem, TextsFile, BBox, NetIR, LabelIR
)
from circuit.graph import UnionFind, PointRegistry, build_graph


def test_union_find_basic_operations():
    uf = UnionFind()
    uf.make(0)
    uf.make(1)
    uf.make(2)
    uf.make(3)

    assert not uf.connected(0, 1)
    uf.union(0, 1)
    assert uf.connected(0, 1)

    uf.union(2, 3)
    assert uf.connected(2, 3)
    assert not uf.connected(0, 2)

    uf.union(1, 2)
    assert uf.connected(0, 3)

    groups = uf.groups()
    # All 4 elements should be in the same root group
    roots = set(uf.find(x) for x in range(4))
    assert len(roots) == 1


def test_point_registry_snap_tolerance():
    reg = PointRegistry(snap_tol=2.0)
    id1 = reg.get_or_create(100.0, 200.0)
    # Exact lookup
    assert reg.get_or_create(100.0, 200.0) == id1
    # Close lookup within 2 px
    assert reg.get_or_create(101.5, 200.5) == id1
    # Far lookup
    id2 = reg.get_or_create(105.0, 200.0)
    assert id2 != id1
    assert len(reg) == 2


def test_build_graph_simple_net():
    # Wire connecting Pin (R1, 1) at (100, 100) to Pin (C1, 1) at (200, 100)
    seg = WireSegment(id="W1", p0=Point(x=100, y=100), p1=Point(x=200, y=100))
    wires = WiresFile(segments=[seg], endpoints=[seg.p0, seg.p1])
    junctions = JunctionsFile(items=[])

    pin_map = {
        "R1": [("1", "A", Point(x=100, y=100))],
        "C1": [("1", "PLUS", Point(x=200, y=100))],
    }

    nets, warnings = build_graph(
        wires=wires,
        junctions=junctions,
        symbols=None,
        texts=None,
        pin_map=pin_map
    )

    assert len(nets) == 1
    net = nets[0]
    assert net.auto_named
    assert ["R1", "1"] in net.pins
    assert ["C1", "1"] in net.pins


def test_build_graph_global_label_merging():
    # Two disconnected wires, both labeled "VCC"
    # Wire 1: (100, 100) to (150, 100)
    # Wire 2: (400, 400) to (450, 400)
    seg1 = WireSegment(id="W1", p0=Point(x=100, y=100), p1=Point(x=150, y=100))
    seg2 = WireSegment(id="W2", p0=Point(x=400, y=400), p1=Point(x=450, y=400))
    wires = WiresFile(
        segments=[seg1, seg2],
        endpoints=[seg1.p0, seg1.p1, seg2.p0, seg2.p1]
    )

    # Texts placed near wire endpoints
    txt1 = TextItem(text="VCC", bbox=BBox(x0=145, y0=95, x1=165, y1=105), conf=1.0)
    txt2 = TextItem(text="VCC", bbox=BBox(x0=445, y0=395, x1=465, y1=405), conf=1.0)
    texts = TextsFile(items=[txt1, txt2])

    pin_map = {
        "R1": [("1", "A", Point(x=100, y=100))],
        "R2": [("1", "A", Point(x=400, y=400))],
    }

    nets, _ = build_graph(
        wires=wires,
        junctions=JunctionsFile(items=[]),
        symbols=None,
        texts=texts,
        pin_map=pin_map
    )

    # Global label merging rule: disconnected sets with same label merge into 1 net!
    assert len(nets) == 1
    assert nets[0].name == "VCC"
    assert not nets[0].auto_named
    assert ["R1", "1"] in nets[0].pins
    assert ["R2", "1"] in nets[0].pins
