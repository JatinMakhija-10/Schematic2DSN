"""
orcad/roundtrip.py  --  S11: Round-trip verification.

After Capture generates the netlist, compare it against the IR.
Canonical form: frozenset of frozenset of (refdes, pin_num).
Net names are ignored -- only connectivity matters.

CLI:
    python -m orcad.roundtrip in/design.json in/capture_netlist.txt
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import FrozenSet, List, Set

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import DesignIR


NetCanonical = FrozenSet[FrozenSet[tuple]]


def ir_to_canonical(ir: DesignIR) -> NetCanonical:
    """
    Convert the IR to canonical form: frozenset of frozenset of (refdes, pin_num).
    Nets with fewer than 2 pins are excluded (they don't form connections).
    """
    nets = set()
    for net in ir.nets:
        pins = frozenset((p[0], p[1]) for p in net.pins if len(p) >= 2)
        if len(pins) >= 2:
            nets.add(pins)
    return frozenset(nets)


def parse_capture_netlist(netlist_path: str) -> NetCanonical:
    """
    Parse a netlist file exported from OrCAD Capture.
    Supports the OrCAD netlist format (tab-delimited or parenthesized).

    Format example (OrCAD Capture simple netlist):
    NET "VCC"
      R1.1
      VCC1.1
    NET "GND"
      C1.2
      GND1.1

    Returns canonical form.
    """
    nets = set()
    current_pins: Set[tuple] = set()

    with open(netlist_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip()
            # Net header
            if re.match(r'^\s*NET\b', line, re.IGNORECASE):
                if len(current_pins) >= 2:
                    nets.add(frozenset(current_pins))
                current_pins = set()
                continue

            # Pin reference: REFDES.PINNUM or REFDES PIN_NUM
            m = re.match(r'^\s+([A-Za-z0-9_]+)\.([A-Za-z0-9]+)', line)
            if m:
                refdes, pin_num = m.group(1).upper(), m.group(2)
                current_pins.add((refdes, pin_num))
                continue

            # Alternative: (REFDES PIN)
            m2 = re.match(r'^\s*\(([A-Za-z0-9_]+)\s+([A-Za-z0-9]+)\)', line)
            if m2:
                refdes, pin_num = m2.group(1).upper(), m2.group(2)
                current_pins.add((refdes, pin_num))

    if len(current_pins) >= 2:
        nets.add(frozenset(current_pins))

    return frozenset(nets)


def compare(ir_canonical: NetCanonical, capture_canonical: NetCanonical) -> dict:
    """
    Compare IR nets with Capture netlist.
    Returns a report dict with match status, missing nets, extra nets.
    """
    ir_set = set(ir_canonical)
    cap_set = set(capture_canonical)

    matched = ir_set & cap_set
    missing_from_capture = ir_set - cap_set  # in IR but not in Capture
    extra_in_capture = cap_set - ir_set      # in Capture but not in IR

    return {
        "match": len(missing_from_capture) == 0 and len(extra_in_capture) == 0,
        "total_ir_nets": len(ir_set),
        "total_capture_nets": len(cap_set),
        "matched": len(matched),
        "missing_from_capture": [sorted(list(n)) for n in missing_from_capture],
        "extra_in_capture": [sorted(list(n)) for n in extra_in_capture],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="S11 Round-trip: compare IR netlist vs Capture netlist"
    )
    parser.add_argument("design_json", help="design.json (IR)")
    parser.add_argument("capture_netlist", help="Netlist exported from Capture")
    args = parser.parse_args()

    with open(args.design_json) as f:
        ir = DesignIR.model_validate(json.load(f))

    ir_canonical = ir_to_canonical(ir)
    cap_canonical = parse_capture_netlist(args.capture_netlist)

    report = compare(ir_canonical, cap_canonical)

    if report["match"]:
        print(f"[roundtrip] ✓ MATCH: {report['matched']} nets identical")
        sys.exit(0)
    else:
        print(f"[roundtrip] ✗ MISMATCH")
        print(f"  IR nets: {report['total_ir_nets']}")
        print(f"  Capture nets: {report['total_capture_nets']}")
        print(f"  Matched: {report['matched']}")
        if report["missing_from_capture"]:
            print(f"  Missing from Capture ({len(report['missing_from_capture'])}):")
            for net in report["missing_from_capture"][:5]:
                print(f"    {net}")
        if report["extra_in_capture"]:
            print(f"  Extra in Capture ({len(report['extra_in_capture'])}):")
            for net in report["extra_in_capture"][:5]:
                print(f"    {net}")
        sys.exit(1)


if __name__ == "__main__":
    main()
