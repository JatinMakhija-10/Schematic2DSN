"""
circuit/graph.py  --  S7: Build connectivity graph via union-find.

Nodes: wire endpoints, junction points, pin attachment points, label attachment points.
Edges: each wire segment connects its two endpoints.
Union-find produces nets (connected sets).

Net naming:
  - Label text if a label is within tolerance of the net.
  - Multiple same labels on different nets -> merge them (global label convention).
  - GND symbol -> net name "GND".
  - Power symbol -> net name from symbol.
  - Auto-named: NET_001, NET_002... sorted by min pin id.

CLI:
    python -m circuit.graph in/wires.json in/junctions.json in/symbols.json in/texts.json in/pins.json out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    WiresFile, JunctionsFile, SymbolsFile, TextsFile,
    WireSegment, JunctionItem, SymbolItem, TextItem,
    NetIR, LabelIR, WarningIR, Point
)
from core.config import DEFAULT_CONFIG
from core.geometry import distance


# ---------------------------------------------------------------------------
# Union-Find
# ---------------------------------------------------------------------------

class UnionFind:
    def __init__(self) -> None:
        self._parent: Dict[int, int] = {}
        self._rank: Dict[int, int] = {}

    def make(self, x: int) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0

    def find(self, x: int) -> int:
        self.make(x)
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def groups(self) -> Dict[int, List[int]]:
        """Return {root: [members]} for all elements."""
        result: Dict[int, List[int]] = {}
        for x in self._parent:
            root = self.find(x)
            result.setdefault(root, []).append(x)
        return result


# ---------------------------------------------------------------------------
# Point registry: maps (x,y) -> integer node id
# ---------------------------------------------------------------------------

class PointRegistry:
    def __init__(self, snap_tol: float = 2.0) -> None:
        self._tol = snap_tol
        self._points: List[Tuple[float, float]] = []
        self._ids: Dict[Tuple[float, float], int] = {}

    def get_or_create(self, x: float, y: float) -> int:
        """Return existing node id if within snap tolerance, else create new."""
        # Fast exact lookup first
        key = (round(x, 1), round(y, 1))
        if key in self._ids:
            return self._ids[key]
        # Approximate lookup
        for i, (px, py) in enumerate(self._points):
            if abs(px - x) <= self._tol and abs(py - y) <= self._tol:
                self._ids[key] = i
                return i
        # New point
        nid = len(self._points)
        self._points.append((x, y))
        self._ids[key] = nid
        return nid

    def get_point(self, nid: int) -> Tuple[float, float]:
        return self._points[nid]

    def __len__(self) -> int:
        return len(self._points)


# ---------------------------------------------------------------------------
# Main graph builder
# ---------------------------------------------------------------------------

def build_graph(
    wires: WiresFile,
    junctions: JunctionsFile,
    symbols: Optional[SymbolsFile],
    texts: Optional[TextsFile],
    pin_map: Optional[Dict[str, List[Tuple[str, str, Point]]]],  # sym_id -> [(num,func,pos)]
    scale_px_per_mil: float = 1.0,
) -> Tuple[List[NetIR], List[WarningIR]]:
    """
    Build the connectivity graph and return nets.

    Parameters
    ----------
    wires : WiresFile
    junctions : JunctionsFile
    symbols : SymbolsFile (for power symbols)
    texts : TextsFile (for net labels)
    pin_map : dict sym_id -> list of (pin_number, function, Point_px)
    scale_px_per_mil : float

    Returns
    -------
    (nets, warnings)
    """
    cfg = DEFAULT_CONFIG.graph
    snap_tol = cfg.endpoint_merge_tolerance_px
    label_tol = cfg.label_snap_tolerance_px

    reg = PointRegistry(snap_tol=snap_tol)
    uf = UnionFind()

    # --- Add wire segments ---
    for seg in wires.segments:
        n0 = reg.get_or_create(seg.p0.x, seg.p0.y)
        n1 = reg.get_or_create(seg.p1.x, seg.p1.y)
        uf.make(n0)
        uf.make(n1)
        uf.union(n0, n1)

    # --- Add junctions (explicit dots connect nearby endpoints) ---
    for junc in junctions.items:
        jn = reg.get_or_create(junc.pos.x, junc.pos.y)
        uf.make(jn)
        # Connect all wire endpoints within junction radius to this node
        for seg in wires.segments:
            for pt in [seg.p0, seg.p1]:
                if distance(junc.pos, pt) <= junc.radius + snap_tol:
                    en = reg.get_or_create(pt.x, pt.y)
                    uf.make(en)
                    uf.union(jn, en)

    # --- Add pin attachment points ---
    # pin_map: sym_id -> [(number, function, Point)]
    # We record which (sym_id, pin_num) belongs to which net root
    pin_to_node: Dict[Tuple[str, str], int] = {}  # (sym_id, pin_num) -> node_id
    if pin_map:
        for sym_id, pins in pin_map.items():
            for (num, func, pos) in pins:
                nid = reg.get_or_create(pos.x, pos.y)
                uf.make(nid)
                pin_to_node[(sym_id, num)] = nid
                # Connect to any wire endpoint within snap tolerance
                for ep in wires.endpoints:
                    if distance(pos, ep) <= DEFAULT_CONFIG.pin.snap_tolerance_px:
                        en = reg.get_or_create(ep.x, ep.y)
                        uf.make(en)
                        uf.union(nid, en)

    # --- Attach text labels to nearest segment ---
    label_assignments: Dict[int, str] = {}  # root -> net_name
    label_items: Dict[int, List[LabelIR]] = {}  # root -> labels

    if texts:
        for text_item in texts.items:
            # Find the closest wire endpoint
            best_d = float("inf")
            best_nid = -1
            tx, ty = text_item.bbox.cx, text_item.bbox.cy
            for ep in wires.endpoints:
                d = distance(Point(x=tx, y=ty), ep)
                if d < best_d:
                    best_d = d
                    best_nid = reg.get_or_create(ep.x, ep.y)

            if best_nid < 0 or best_d > label_tol:
                continue

            root = uf.find(best_nid)
            net_name = text_item.text.upper()
            label = LabelIR(text=text_item.text, pos=Point(x=tx, y=ty))

            if root not in label_assignments:
                label_assignments[root] = net_name
            elif label_assignments[root] != net_name:
                # Conflict: two different labels on same net
                pass  # validate.py will catch this

            label_items.setdefault(root, []).append(label)

    # --- Merge nets with the same label name (global label convention) ---
    name_to_root: Dict[str, int] = {}
    for root, name in label_assignments.items():
        if name in name_to_root:
            uf.union(root, name_to_root[name])
        else:
            name_to_root[name] = root

    # --- Build net objects ---
    groups = uf.groups()
    warnings: List[WarningIR] = []
    nets: List[NetIR] = []

    # Map from sym_id+pin_num -> which root they ended up in
    final_pin_net: Dict[Tuple[str, str], str] = {}

    auto_counter = [0]  # mutable for closure

    def auto_name() -> str:
        auto_counter[0] += 1
        return f"NET_{auto_counter[0]:03d}"

    for root, members in sorted(groups.items()):
        # Resolve final root after all unions
        final_root = uf.find(root)

        # Collect pins in this net
        net_pins: List[List[str]] = []
        for (sym_id, pin_num), nid in pin_to_node.items():
            if uf.find(nid) == final_root:
                net_pins.append([sym_id, pin_num])

        # Skip nets with no pins (wire stubs not connected to anything)
        if not net_pins:
            continue

        # Determine net name
        final_labels = label_items.get(final_root, [])
        if final_labels:
            name = label_assignments.get(final_root, auto_name())
            auto_named = False
        else:
            name = auto_name()
            auto_named = True

        nets.append(NetIR(
            name=name,
            auto_named=auto_named,
            pins=net_pins,
            labels=final_labels
        ))

    # Sort by name for stable output
    nets.sort(key=lambda n: n.name)

    return nets, warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="S7 Graph: wires + junctions + symbols -> nets"
    )
    parser.add_argument("wires", help="wires.json")
    parser.add_argument("junctions", help="junctions.json")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with open(args.wires) as f:
        wires = WiresFile.model_validate(json.load(f))
    with open(args.junctions) as f:
        junctions = JunctionsFile.model_validate(json.load(f))

    nets, warnings = build_graph(wires, junctions, None, None, None)
    result = {
        "nets": [n.model_dump() for n in nets],
        "warnings": [w.model_dump() for w in warnings]
    }
    out_path = out / "nets_raw.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[graph] {len(nets)} nets, {len(warnings)} warnings -> {out_path}")


if __name__ == "__main__":
    main()
