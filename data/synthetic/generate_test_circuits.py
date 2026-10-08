"""
data/synthetic/generate_test_circuits.py  --  KiCad test generator.

Generates synthetic test schematics as design IR JSON files with
ground-truth netlists. Uses pure Python (no KiCad dependency).

Circuits generated (in increasing difficulty):
  1. voltage_divider    : R1-R2 divider (VCC -> R1 -> R2 -> GND)
  2. rc_filter          : R1+C1 low-pass (VCC -> R1 -> C1 -> GND)
  3. led_driver         : R1+D1+LED1 (VCC -> R1 -> D1 -> GND, LED indicator)
  4. inverting_opamp    : OPAMP with R_in + R_fb (classic inverter)
  5. common_emitter     : NPN transistor amplifier stage

Each generates:
  - synthetic/<name>/design.json   (the IR ground truth)
  - synthetic/<name>/netlist.json  (canonical set-of-sets for comparison)

CLI:
    python -m data.synthetic.generate_test_circuits
    python -m data.synthetic.generate_test_circuits --circuit voltage_divider
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.models import (
    DesignIR, DesignInfo, ComponentIR, PinIR, NetIR, LabelIR,
    WarningIR, DesignMetadata, Point
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _p(x: int, y: int) -> Point:
    return Point(x=x, y=y)


def _resistor(rid: str, value: str, x: int, y: int,
               pin1_net: str, pin2_net: str, rotation: int = 0) -> ComponentIR:
    off = 100
    if rotation == 0:
        p1_pos = _p(x - off, y)
        p2_pos = _p(x + off, y)
    else:
        p1_pos = _p(x, y + off)
        p2_pos = _p(x, y - off)
    return ComponentIR(
        id=rid, symbol_class="RESISTOR", value=value,
        unit=1, position=_p(x, y), rotation=rotation, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="A", pos=p1_pos, net=pin1_net),
            PinIR(number="2", function="B", pos=p2_pos, net=pin2_net),
        ]
    )


def _capacitor(cid: str, value: str, x: int, y: int,
                plus_net: str, minus_net: str, rotation: int = 90) -> ComponentIR:
    off = 100
    if rotation == 90:
        p1_pos = _p(x, y + off)
        p2_pos = _p(x, y - off)
    else:
        p1_pos = _p(x - off, y)
        p2_pos = _p(x + off, y)
    return ComponentIR(
        id=cid, symbol_class="CAPACITOR", value=value,
        unit=1, position=_p(x, y), rotation=rotation, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="PLUS", pos=p1_pos, net=plus_net),
            PinIR(number="2", function="MINUS", pos=p2_pos, net=minus_net),
        ]
    )


def _diode(did: str, value: str, x: int, y: int,
            anode_net: str, cathode_net: str) -> ComponentIR:
    return ComponentIR(
        id=did, symbol_class="DIODE", value=value,
        unit=1, position=_p(x, y), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="ANODE", pos=_p(x - 100, y), net=anode_net),
            PinIR(number="2", function="CATHODE", pos=_p(x + 100, y), net=cathode_net),
        ]
    )


def _power(pwr_id: str, sym_class: str, net_name: str, x: int, y: int) -> ComponentIR:
    dy = -100 if sym_class == "VCC" else 100
    return ComponentIR(
        id=pwr_id, symbol_class=sym_class, value="",
        unit=1, position=_p(x, y), rotation=0, mirror=False,
        confidence=1.0,
        pins=[PinIR(number="1", function="PWR", pos=_p(x, y + dy), net=net_name)]
    )


def _net(name: str, auto: bool, pins: List, labels: List | None = None) -> NetIR:
    return NetIR(
        name=name,
        auto_named=auto,
        pins=pins,
        labels=labels or []
    )


# ---------------------------------------------------------------------------
# Circuit builders
# ---------------------------------------------------------------------------

def voltage_divider() -> DesignIR:
    """VCC -> R1 -> mid -> R2 -> GND"""
    r1 = _resistor("R1", "10k", 4000, 3000, "VCC", "MID")
    r2 = _resistor("R2", "10k", 4600, 3000, "MID", "GND")
    vcc = _power("VCC1", "VCC", "VCC", 3800, 3200)
    gnd = _power("GND1", "GROUND", "GND", 4800, 2800)

    nets = [
        _net("VCC", False, [["R1", "1"], ["VCC1", "1"]],
             [LabelIR(text="VCC", pos=_p(3800, 3200))]),
        _net("MID", True, [["R1", "2"], ["R2", "1"]]),
        _net("GND", False, [["R2", "2"], ["GND1", "1"]],
             [LabelIR(text="GND", pos=_p(4800, 2800))]),
    ]
    return DesignIR(
        design=DesignInfo(name="voltage_divider"),
        components=[r1, r2, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector",
                                confidence=1.0, ocr_confidence=1.0)
    )


def rc_filter() -> DesignIR:
    """VCC -> R1 -> out -> C1 -> GND"""
    r1 = _resistor("R1", "1k", 4000, 3000, "VCC", "OUT")
    c1 = _capacitor("C1", "100nF", 4600, 3000, "OUT", "GND")
    vcc = _power("VCC1", "VCC", "VCC", 3800, 3200)
    gnd = _power("GND1", "GROUND", "GND", 4800, 2800)

    nets = [
        _net("VCC", False, [["R1", "1"], ["VCC1", "1"]]),
        _net("OUT", True, [["R1", "2"], ["C1", "1"]]),
        _net("GND", False, [["C1", "2"], ["GND1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="rc_filter"),
        components=[r1, c1, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector",
                                confidence=1.0, ocr_confidence=1.0)
    )


def led_driver() -> DesignIR:
    """VCC -> R1 -> anode -> D1(LED) -> cathode -> GND"""
    r1 = _resistor("R1", "330R", 4000, 3000, "VCC", "NET_001")
    d1 = ComponentIR(
        id="D1", symbol_class="LED", value="RED",
        unit=1, position=_p(4600, 3000), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="ANODE", pos=_p(4500, 3000), net="NET_001"),
            PinIR(number="2", function="CATHODE", pos=_p(4700, 3000), net="GND"),
        ]
    )
    vcc = _power("VCC1", "VCC", "VCC", 3800, 3200)
    gnd = _power("GND1", "GROUND", "GND", 4800, 2800)

    nets = [
        _net("VCC", False, [["R1", "1"], ["VCC1", "1"]]),
        _net("NET_001", True, [["R1", "2"], ["D1", "1"]]),
        _net("GND", False, [["D1", "2"], ["GND1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="led_driver"),
        components=[r1, d1, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector",
                                confidence=1.0, ocr_confidence=1.0)
    )


def inverting_opamp() -> DesignIR:
    """Inverting amplifier: Vin -> Rin -> IN_MINUS, Rfb from OUT to IN_MINUS, IN_PLUS -> GND"""
    r_in = _resistor("R1", "10k", 3800, 3100, "VIN", "IN_MINUS")
    r_fb = _resistor("R2", "100k", 4600, 2800, "IN_MINUS", "VOUT", rotation=0)
    u1 = ComponentIR(
        id="U1", symbol_class="OPAMP", value="LM741",
        unit=1, position=_p(4300, 3000), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="IN_MINUS", pos=_p(4100, 3100), net="IN_MINUS"),
            PinIR(number="2", function="IN_PLUS", pos=_p(4100, 2900), net="GND"),
            PinIR(number="3", function="VS_PLUS", pos=_p(4300, 3200), net="VCC"),
            PinIR(number="4", function="VS_MINUS", pos=_p(4300, 2800), net="VEE"),
            PinIR(number="5", function="OUT", pos=_p(4500, 3000), net="VOUT"),
        ]
    )
    vcc = _power("VCC1", "VCC", "VCC", 4200, 3400)
    gnd1 = _power("GND1", "GROUND", "GND", 4100, 2700)
    gnd2 = _power("GND2", "GROUND", "VEE", 4300, 2600)

    nets = [
        _net("VIN", False, [["R1", "1"]], [LabelIR(text="VIN", pos=_p(3700, 3100))]),
        _net("IN_MINUS", True, [["R1", "2"], ["U1", "1"], ["R2", "1"]]),
        _net("GND", False, [["U1", "2"], ["GND1", "1"]]),
        _net("VCC", False, [["U1", "3"], ["VCC1", "1"]]),
        _net("VEE", False, [["U1", "4"], ["GND2", "1"]]),
        _net("VOUT", False, [["U1", "5"], ["R2", "2"]], [LabelIR(text="VOUT", pos=_p(4700, 3000))]),
    ]
    return DesignIR(
        design=DesignInfo(name="inverting_opamp"),
        components=[r_in, r_fb, u1, vcc, gnd1, gnd2],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector",
                                confidence=1.0, ocr_confidence=1.0)
    )


def common_emitter() -> DesignIR:
    """NPN common emitter: VCC -> Rc -> collector, base via Rb from VIN, emitter -> GND"""
    rc = _resistor("R1", "1k", 4300, 2600, "VCC", "COLLECTOR", rotation=90)
    rb = _resistor("R2", "100k", 3800, 3000, "VIN", "BASE")
    q1 = ComponentIR(
        id="Q1", symbol_class="NPN", value="2N2222",
        unit=1, position=_p(4300, 3000), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="BASE", pos=_p(4150, 3000), net="BASE"),
            PinIR(number="2", function="COLLECTOR", pos=_p(4400, 2850), net="COLLECTOR"),
            PinIR(number="3", function="EMITTER", pos=_p(4400, 3150), net="GND"),
        ]
    )
    vcc = _power("VCC1", "VCC", "VCC", 4300, 2400)
    gnd = _power("GND1", "GROUND", "GND", 4400, 3300)

    nets = [
        _net("VCC", False, [["R1", "1"], ["VCC1", "1"]]),
        _net("COLLECTOR", True, [["R1", "2"], ["Q1", "2"]]),
        _net("VIN", False, [["R2", "1"]], [LabelIR(text="VIN", pos=_p(3700, 3000))]),
        _net("BASE", True, [["R2", "2"], ["Q1", "1"]]),
        _net("GND", False, [["Q1", "3"], ["GND1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="common_emitter"),
        components=[rc, rb, q1, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector",
                                confidence=1.0, ocr_confidence=1.0)
    )


# ---------------------------------------------------------------------------
# Canonical netlist export
# ---------------------------------------------------------------------------

def ir_to_netlist(ir: DesignIR) -> List[List[List[str]]]:
    """Export nets as list of lists of [refdes, pin_num] for comparison."""
    return [
        sorted([list(p) for p in net.pins])
        for net in ir.nets
        if len(net.pins) >= 2
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

CIRCUITS: Dict[str, Callable[[], DesignIR]] = {
    "voltage_divider": voltage_divider,
    "rc_filter": rc_filter,
    "led_driver": led_driver,
    "inverting_opamp": inverting_opamp,
    "common_emitter": common_emitter,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic test circuit IRs and ground-truth netlists."
    )
    parser.add_argument(
        "--circuit", choices=list(CIRCUITS.keys()),
        help="Generate a specific circuit only (default: all)"
    )
    args = parser.parse_args()

    base = Path(__file__).parent

    circuits_to_gen = [args.circuit] if args.circuit else list(CIRCUITS.keys())

    for name in circuits_to_gen:
        fn = CIRCUITS[name]
        ir = fn()
        out_dir = base / name
        out_dir.mkdir(parents=True, exist_ok=True)

        design_path = out_dir / "design.json"
        design_path.write_text(ir.model_dump_json(indent=2), encoding="utf-8")

        netlist = ir_to_netlist(ir)
        netlist_path = out_dir / "netlist.json"
        netlist_path.write_text(json.dumps(netlist, indent=2), encoding="utf-8")

        print(f"[gen] {name}: {len(ir.components)} components, "
              f"{len(ir.nets)} nets -> {out_dir}")


if __name__ == "__main__":
    main()
