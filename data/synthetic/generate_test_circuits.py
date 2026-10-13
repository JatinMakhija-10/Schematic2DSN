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
from data.synthetic.render_synthetic import render_ir_to_pdf, render_ir_to_png


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


def _inductor(lid: str, value: str, x: int, y: int,
              pin1_net: str, pin2_net: str, rotation: int = 0) -> ComponentIR:
    off = 100
    if rotation == 0:
        p1_pos = _p(x - off, y)
        p2_pos = _p(x + off, y)
    else:
        p1_pos = _p(x, y + off)
        p2_pos = _p(x, y - off)
    return ComponentIR(
        id=lid, symbol_class="INDUCTOR", value=value,
        unit=1, position=_p(x, y), rotation=rotation, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="A", pos=p1_pos, net=pin1_net),
            PinIR(number="2", function="B", pos=p2_pos, net=pin2_net),
        ]
    )


def _transistor(qid: str, sym_class: str, value: str, x: int, y: int,
                base_net: str, collector_net: str, emitter_net: str, rotation: int = 0) -> ComponentIR:
    return ComponentIR(
        id=qid, symbol_class=sym_class, value=value,
        unit=1, position=_p(x, y), rotation=rotation, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="BASE", pos=_p(x - 150, y), net=base_net),
            PinIR(number="2", function="COLLECTOR", pos=_p(x + 100, y + 150), net=collector_net),
            PinIR(number="3", function="EMITTER", pos=_p(x + 100, y - 150), net=emitter_net),
        ]
    )


def _fet(mid: str, sym_class: str, value: str, x: int, y: int,
         gate_net: str, drain_net: str, source_net: str, rotation: int = 0) -> ComponentIR:
    return ComponentIR(
        id=mid, symbol_class=sym_class, value=value,
        unit=1, position=_p(x, y), rotation=rotation, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="GATE", pos=_p(x - 150, y), net=gate_net),
            PinIR(number="2", function="DRAIN", pos=_p(x + 100, y + 150), net=drain_net),
            PinIR(number="3", function="SOURCE", pos=_p(x + 100, y - 150), net=source_net),
        ]
    )


def _connector(jid: str, x: int, y: int, p1_net: str, p2_net: str) -> ComponentIR:
    return ComponentIR(
        id=jid, symbol_class="CONNECTOR", value="HEADER_1X2",
        unit=1, position=_p(x, y), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="P1", pos=_p(x + 100, y + 50), net=p1_net),
            PinIR(number="2", function="P2", pos=_p(x + 100, y - 50), net=p2_net),
        ]
    )


def _crystal(yid: str, value: str, x: int, y: int, p1_net: str, p2_net: str) -> ComponentIR:
    return ComponentIR(
        id=yid, symbol_class="CRYSTAL", value=value,
        package="HC-49S",
        unit=1, position=_p(x, y), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="XTAL1", pos=_p(x - 100, y), net=p1_net, electrical_type="PASSIVE"),
            PinIR(number="2", function="XTAL2", pos=_p(x + 100, y), net=p2_net, electrical_type="PASSIVE"),
        ]
    )


def _switch(swid: str, value: str, x: int, y: int, p1_net: str, p2_net: str) -> ComponentIR:
    return ComponentIR(
        id=swid, symbol_class="SWITCH", value=value,
        package="SPST-TACT",
        unit=1, position=_p(x, y), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="COM", pos=_p(x - 100, y), net=p1_net, electrical_type="PASSIVE"),
            PinIR(number="2", function="NO", pos=_p(x + 100, y), net=p2_net, electrical_type="PASSIVE"),
        ]
    )


def _ic_timer555(uid: str, value: str, x: int, y: int, pin_nets: Dict[str, str]) -> ComponentIR:
    pins = [
        PinIR(number="1", function="GND", pos=_p(x - 150, y - 90), net=pin_nets.get("1"), electrical_type="POWER", side="LEFT"),
        PinIR(number="2", function="TRIG", pos=_p(x - 150, y - 30), net=pin_nets.get("2"), electrical_type="INPUT", side="LEFT"),
        PinIR(number="3", function="OUT", pos=_p(x + 150, y - 30), net=pin_nets.get("3"), electrical_type="OUTPUT", side="RIGHT"),
        PinIR(number="4", function="RESET", pos=_p(x - 150, y + 90), net=pin_nets.get("4"), electrical_type="INPUT", side="LEFT"),
        PinIR(number="5", function="CTRL", pos=_p(x + 150, y - 90), net=pin_nets.get("5"), electrical_type="PASSIVE", side="RIGHT"),
        PinIR(number="6", function="THRESH", pos=_p(x - 150, y + 30), net=pin_nets.get("6"), electrical_type="INPUT", side="LEFT"),
        PinIR(number="7", function="DISCH", pos=_p(x + 150, y + 30), net=pin_nets.get("7"), electrical_type="OUTPUT", side="RIGHT"),
        PinIR(number="8", function="VCC", pos=_p(x + 150, y + 90), net=pin_nets.get("8"), electrical_type="POWER", side="RIGHT"),
    ]
    return ComponentIR(
        id=uid, symbol_class="TIMER_555", value=value, package="DIP-8",
        description="Precision Timer IC",
        unit=1, position=_p(x, y), rotation=0, mirror=False, confidence=1.0, pins=pins
    )


def _regulator_switching(uid: str, value: str, x: int, y: int, pin_nets: Dict[str, str]) -> ComponentIR:
    pins = [
        PinIR(number="1", function="VIN", pos=_p(x - 150, y + 60), net=pin_nets.get("1"), electrical_type="POWER", side="LEFT"),
        PinIR(number="2", function="OUT", pos=_p(x + 150, y + 60), net=pin_nets.get("2"), electrical_type="OUTPUT", side="RIGHT"),
        PinIR(number="3", function="GND", pos=_p(x, y - 120), net=pin_nets.get("3"), electrical_type="POWER", side="BOTTOM"),
        PinIR(number="4", function="FB", pos=_p(x + 150, y - 40), net=pin_nets.get("4"), electrical_type="INPUT", side="RIGHT"),
        PinIR(number="5", function="ON_OFF", pos=_p(x - 150, y - 40), net=pin_nets.get("5"), electrical_type="INPUT", side="LEFT"),
    ]
    return ComponentIR(
        id=uid, symbol_class="REGULATOR", value=value, package="TO-263-5",
        description="Step-Down Voltage Regulator",
        unit=1, position=_p(x, y), rotation=0, mirror=False, confidence=1.0, pins=pins
    )


def _mcu_atmega328(uid: str, value: str, x: int, y: int, pin_nets: Dict[str, str]) -> ComponentIR:
    pins = [
        PinIR(number="1", function="RESET", pos=_p(x - 180, y + 140), net=pin_nets.get("1"), electrical_type="INPUT", side="LEFT"),
        PinIR(number="2", function="PD0_RXD", pos=_p(x - 180, y + 100), net=pin_nets.get("2"), electrical_type="BIDIRECTIONAL", side="LEFT"),
        PinIR(number="3", function="PD1_TXD", pos=_p(x - 180, y + 60), net=pin_nets.get("3"), electrical_type="BIDIRECTIONAL", side="LEFT"),
        PinIR(number="7", function="VCC", pos=_p(x - 180, y + 20), net=pin_nets.get("7"), electrical_type="POWER", side="LEFT"),
        PinIR(number="8", function="GND", pos=_p(x - 180, y - 20), net=pin_nets.get("8"), electrical_type="POWER", side="LEFT"),
        PinIR(number="9", function="XTAL1", pos=_p(x - 180, y - 60), net=pin_nets.get("9"), electrical_type="INPUT", side="LEFT"),
        PinIR(number="10", function="XTAL2", pos=_p(x - 180, y - 100), net=pin_nets.get("10"), electrical_type="OUTPUT", side="LEFT"),
        PinIR(number="19", function="PB5_SCK", pos=_p(x + 180, y + 100), net=pin_nets.get("19"), electrical_type="BIDIRECTIONAL", side="RIGHT"),
        PinIR(number="20", function="AVCC", pos=_p(x + 180, y + 60), net=pin_nets.get("20"), electrical_type="POWER", side="RIGHT"),
        PinIR(number="21", function="AREF", pos=_p(x + 180, y + 20), net=pin_nets.get("21"), electrical_type="INPUT", side="RIGHT"),
        PinIR(number="22", function="AGND", pos=_p(x + 180, y - 20), net=pin_nets.get("22"), electrical_type="POWER", side="RIGHT"),
    ]
    return ComponentIR(
        id=uid, symbol_class="MICROCONTROLLER", value=value, package="DIP-28",
        description="8-bit AVR Microcontroller",
        unit=1, position=_p(x, y), rotation=0, mirror=False, confidence=1.0, pins=pins
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


def bjt_astable() -> DesignIR:
    """BJT Astable Multivibrator oscillator circuit."""
    r1 = _resistor("R1", "1k", 3800, 2600, "VCC", "NET_C1", rotation=90)
    r2 = _resistor("R2", "47k", 4100, 2600, "VCC", "NET_B1", rotation=90)
    r3 = _resistor("R3", "47k", 4400, 2600, "VCC", "NET_B2", rotation=90)
    r4 = _resistor("R4", "1k", 4700, 2600, "VCC", "NET_C2", rotation=90)
    c1 = _capacitor("C1", "10uF", 4000, 2900, "NET_C1", "NET_B2", rotation=0)
    c2 = _capacitor("C2", "10uF", 4500, 2900, "NET_C2", "NET_B1", rotation=0)
    q1 = _transistor("Q1", "NPN", "2N2222", 3900, 3200, "NET_B1", "NET_C1", "GND")
    q2 = _transistor("Q2", "NPN", "2N2222", 4600, 3200, "NET_B2", "NET_C2", "GND")
    vcc = _power("VCC1", "VCC", "VCC", 4250, 2400)
    gnd = _power("GND1", "GROUND", "GND", 4250, 3500)

    nets = [
        _net("VCC", False, [["R1", "1"], ["R2", "1"], ["R3", "1"], ["R4", "1"], ["VCC1", "1"]]),
        _net("NET_C1", True, [["R1", "2"], ["Q1", "2"], ["C1", "1"]]),
        _net("NET_B1", True, [["R2", "2"], ["Q1", "1"], ["C2", "2"]]),
        _net("NET_B2", True, [["R3", "2"], ["Q2", "1"], ["C1", "2"]]),
        _net("NET_C2", True, [["R4", "2"], ["Q2", "2"], ["C2", "1"]]),
        _net("GND", False, [["Q1", "3"], ["Q2", "3"], ["GND1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="bjt_astable"),
        components=[r1, r2, r3, r4, c1, c2, q1, q2, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector", confidence=1.0, ocr_confidence=1.0)
    )


def h_bridge() -> DesignIR:
    """H-Bridge Motor Driver with 4 MOSFETs and terminal connector."""
    m1 = _fet("M1", "NMOS", "2N7000", 3800, 3200, "CTRL_LO_L", "MOTOR_A", "GND")
    m2 = _fet("M2", "PMOS", "IRF9540", 3800, 2700, "CTRL_HI_L", "MOTOR_A", "VCC")
    m3 = _fet("M3", "NMOS", "2N7000", 4600, 3200, "CTRL_LO_R", "MOTOR_B", "GND")
    m4 = _fet("M4", "PMOS", "IRF9540", 4600, 2700, "CTRL_HI_R", "MOTOR_B", "VCC")
    r1 = _resistor("R1", "10k", 3600, 2700, "VCC", "CTRL_HI_L")
    r2 = _resistor("R2", "10k", 3600, 3200, "CTRL_LO_L", "GND")
    r3 = _resistor("R3", "10k", 4800, 2700, "VCC", "CTRL_HI_R")
    r4 = _resistor("R4", "10k", 4800, 3200, "CTRL_LO_R", "GND")
    j1 = _connector("J1", 4200, 2950, "MOTOR_A", "MOTOR_B")
    vcc = _power("VCC1", "VCC", "VCC", 4200, 2400)
    gnd = _power("GND1", "GROUND", "GND", 4200, 3500)

    nets = [
        _net("VCC", False, [["M2", "3"], ["M4", "3"], ["R1", "1"], ["R3", "1"], ["VCC1", "1"]]),
        _net("GND", False, [["M1", "3"], ["M3", "3"], ["R2", "2"], ["R4", "2"], ["GND1", "1"]]),
        _net("MOTOR_A", True, [["M1", "2"], ["M2", "2"], ["J1", "1"]]),
        _net("MOTOR_B", True, [["M3", "2"], ["M4", "2"], ["J1", "2"]]),
        _net("CTRL_HI_L", False, [["M2", "1"], ["R1", "2"]], [LabelIR(text="CTRL_HI_L", pos=_p(3600, 2700))]),
        _net("CTRL_LO_L", False, [["M1", "1"], ["R2", "1"]], [LabelIR(text="CTRL_LO_L", pos=_p(3600, 3200))]),
        _net("CTRL_HI_R", False, [["M4", "1"], ["R3", "2"]], [LabelIR(text="CTRL_HI_R", pos=_p(4800, 2700))]),
        _net("CTRL_LO_R", False, [["M3", "1"], ["R4", "1"]], [LabelIR(text="CTRL_LO_R", pos=_p(4800, 3200))]),
    ]
    return DesignIR(
        design=DesignInfo(name="h_bridge"),
        components=[m1, m2, m3, m4, r1, r2, r3, r4, j1, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector", confidence=1.0, ocr_confidence=1.0)
    )


def diff_amp() -> DesignIR:
    """Differential Amplifier stage with OPAMP and matched resistors."""
    r1 = _resistor("R1", "10k", 3700, 2900, "VIN_NEG", "IN_MINUS")
    r2 = _resistor("R2", "100k", 4400, 2700, "IN_MINUS", "VOUT")
    r3 = _resistor("R3", "10k", 3700, 3100, "VIN_POS", "IN_PLUS")
    r4 = _resistor("R4", "100k", 4200, 3300, "IN_PLUS", "GND")
    u1 = ComponentIR(
        id="U1", symbol_class="OPAMP", value="TL072",
        unit=1, position=_p(4200, 3000), rotation=0, mirror=False,
        confidence=1.0,
        pins=[
            PinIR(number="1", function="IN_MINUS", pos=_p(4000, 2900), net="IN_MINUS"),
            PinIR(number="2", function="IN_PLUS", pos=_p(4000, 3100), net="IN_PLUS"),
            PinIR(number="3", function="VS_PLUS", pos=_p(4200, 2800), net="VCC"),
            PinIR(number="4", function="VS_MINUS", pos=_p(4200, 3200), net="VEE"),
            PinIR(number="5", function="OUT", pos=_p(4400, 3000), net="VOUT"),
        ]
    )
    vcc = _power("VCC1", "VCC", "VCC", 4200, 2600)
    gnd1 = _power("GND1", "GROUND", "GND", 4200, 3500)
    gnd2 = _power("GND2", "GROUND", "VEE", 4350, 3500)

    nets = [
        _net("VIN_NEG", False, [["R1", "1"]], [LabelIR(text="VIN_NEG", pos=_p(3600, 2900))]),
        _net("VIN_POS", False, [["R3", "1"]], [LabelIR(text="VIN_POS", pos=_p(3600, 3100))]),
        _net("IN_MINUS", True, [["R1", "2"], ["R2", "1"], ["U1", "1"]]),
        _net("IN_PLUS", True, [["R3", "2"], ["R4", "1"], ["U1", "2"]]),
        _net("VOUT", False, [["R2", "2"], ["U1", "5"]], [LabelIR(text="VOUT", pos=_p(4500, 3000))]),
        _net("VCC", False, [["U1", "3"], ["VCC1", "1"]]),
        _net("VEE", False, [["U1", "4"], ["GND2", "1"]]),
        _net("GND", False, [["R4", "2"], ["GND1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="diff_amp"),
        components=[r1, r2, r3, r4, u1, vcc, gnd1, gnd2],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector", confidence=1.0, ocr_confidence=1.0)
    )


def bandpass_filter() -> DesignIR:
    """RLC Bandpass Filter."""
    r1 = _resistor("R1", "50R", 3800, 3000, "VIN", "MID_NODE")
    l1 = _inductor("L1", "10uH", 4300, 3000, "MID_NODE", "OUT")
    c1 = _capacitor("C1", "100pF", 4300, 3300, "OUT", "GND", rotation=90)
    vcc = _power("VCC1", "VCC", "VIN", 3600, 3200)
    gnd = _power("GND1", "GROUND", "GND", 4300, 3500)

    nets = [
        _net("VIN", False, [["R1", "1"], ["VCC1", "1"]], [LabelIR(text="VIN", pos=_p(3600, 3200))]),
        _net("MID_NODE", True, [["R1", "2"], ["L1", "1"]]),
        _net("OUT", False, [["L1", "2"], ["C1", "1"]], [LabelIR(text="OUT", pos=_p(4500, 3000))]),
        _net("GND", False, [["C1", "2"], ["GND1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="bandpass_filter"),
        components=[r1, l1, c1, vcc, gnd],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector", confidence=1.0, ocr_confidence=1.0)
    )


def timer_555_astable() -> DesignIR:
    """NE555 Timer IC configured as an astable multivibrator clock generator."""
    u1 = _ic_timer555("U1", "NE555", 4200, 3000, {
        "1": "GND",
        "2": "TRIG_NODE",
        "3": "OUT_NODE",
        "4": "VCC",
        "5": "CTRL_NODE",
        "6": "TRIG_NODE",
        "7": "DISCH_NODE",
        "8": "VCC",
    })
    r1 = _resistor("R1", "10k", 4200, 3400, "VCC", "DISCH_NODE", rotation=90)
    r2 = _resistor("R2", "47k", 3800, 3200, "DISCH_NODE", "TRIG_NODE", rotation=90)
    c1 = _capacitor("C1", "10uF", 3800, 2600, "TRIG_NODE", "GND", rotation=90)
    c2 = _capacitor("C2", "10nF", 4600, 2600, "CTRL_NODE", "GND", rotation=90)
    r3 = _resistor("R3", "330R", 4700, 2970, "OUT_NODE", "LED_NODE", rotation=0)
    d1 = _diode("D1", "LED_RED", 5000, 2970, "LED_NODE", "GND")
    vcc1 = _power("VCC1", "VCC", "VCC", 4350, 3600)
    gnd1 = _power("GND1", "GROUND", "GND", 4050, 2300)

    nets = [
        _net("VCC", False, [["VCC1", "1"], ["U1", "4"], ["U1", "8"], ["R1", "1"]], [LabelIR(text="VCC", pos=_p(4350, 3600))]),
        _net("GND", False, [["GND1", "1"], ["U1", "1"], ["C1", "2"], ["C2", "2"], ["D1", "2"]], [LabelIR(text="GND", pos=_p(4050, 2300))]),
        _net("DISCH_NODE", True, [["R1", "2"], ["R2", "1"], ["U1", "7"]]),
        _net("TRIG_NODE", True, [["R2", "2"], ["C1", "1"], ["U1", "2"], ["U1", "6"]]),
        _net("CTRL_NODE", True, [["U1", "5"], ["C2", "1"]]),
        _net("OUT_NODE", False, [["U1", "3"], ["R3", "1"]], [LabelIR(text="CLK_OUT", pos=_p(4500, 3050))]),
        _net("LED_NODE", True, [["R3", "2"], ["D1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="timer_555_astable"),
        components=[u1, r1, r2, c1, c2, r3, d1, vcc1, gnd1],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector", confidence=1.0, ocr_confidence=1.0)
    )


def buck_converter() -> DesignIR:
    """Step-down switching regulator based on LM2596-ADJ with catch diode and LC filter."""
    u1 = _regulator_switching("U1", "LM2596-ADJ", 4200, 3000, {
        "1": "VIN",
        "2": "SW_NODE",
        "3": "GND",
        "4": "FB_NODE",
        "5": "GND",
    })
    cin = _capacitor("CIN", "100uF", 3700, 3000, "VIN", "GND", rotation=90)
    d1 = _diode("D1", "1N5822", 4450, 2750, "GND", "SW_NODE")
    l1 = _inductor("L1", "33uH", 4700, 3060, "SW_NODE", "VOUT", rotation=0)
    cout = _capacitor("COUT", "220uF", 5100, 2800, "VOUT", "GND", rotation=90)
    r1 = _resistor("R1", "3.1k", 4800, 2600, "VOUT", "FB_NODE", rotation=90)
    r2 = _resistor("R2", "1.0k", 4800, 2300, "FB_NODE", "GND", rotation=90)
    vcc1 = _power("VCC1", "VCC", "VIN", 3700, 3350)
    gnd1 = _power("GND1", "GROUND", "GND", 4200, 2200)

    nets = [
        _net("VIN", False, [["VCC1", "1"], ["CIN", "1"], ["U1", "1"]], [LabelIR(text="VIN_24V", pos=_p(3650, 3350))]),
        _net("SW_NODE", True, [["U1", "2"], ["D1", "2"], ["L1", "1"]]),
        _net("VOUT", False, [["L1", "2"], ["COUT", "1"], ["R1", "1"]], [LabelIR(text="VOUT_5V", pos=_p(5150, 3100))]),
        _net("FB_NODE", True, [["R1", "2"], ["R2", "1"], ["U1", "4"]]),
        _net("GND", False, [["GND1", "1"], ["CIN", "2"], ["U1", "3"], ["U1", "5"], ["D1", "1"], ["COUT", "2"], ["R2", "2"]], [LabelIR(text="GND", pos=_p(4200, 2200))]),
    ]
    return DesignIR(
        design=DesignInfo(name="buck_converter"),
        components=[u1, cin, d1, l1, cout, r1, r2, vcc1, gnd1],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector", confidence=1.0, ocr_confidence=1.0)
    )


def mcu_minimum_system() -> DesignIR:
    """ATmega328P Microcontroller minimum system with crystal clock, reset, status LED, and UART."""
    u1 = _mcu_atmega328("U1", "ATMEGA328P", 4200, 3000, {
        "1": "RESET_NET",
        "2": "MCU_RX",
        "3": "MCU_TX",
        "7": "VCC",
        "8": "GND",
        "9": "XTAL1_NET",
        "10": "XTAL2_NET",
        "19": "LED_DRIVE",
        "20": "VCC",
        "21": "AREF_NET",
        "22": "GND",
    })
    r1 = _resistor("R1", "10k", 3800, 3400, "VCC", "RESET_NET", rotation=90)
    sw1 = _switch("SW1", "RESET_BTN", 3800, 3140, "RESET_NET", "GND")
    y1 = _crystal("Y1", "16MHz", 3750, 2750, "XTAL1_NET", "XTAL2_NET")
    c1 = _capacitor("C1", "22pF", 3650, 2500, "XTAL1_NET", "GND", rotation=90)
    c2 = _capacitor("C2", "22pF", 3850, 2500, "XTAL2_NET", "GND", rotation=90)
    c3 = _capacitor("C3", "100nF", 4020, 2700, "VCC", "GND", rotation=90)
    c4 = _capacitor("C4", "100nF", 4600, 2700, "AREF_NET", "GND", rotation=90)
    r2 = _resistor("R2", "1k", 4700, 3100, "LED_DRIVE", "LED_NET", rotation=0)
    d1 = _diode("D1", "LED_STAT", 5000, 3100, "LED_NET", "GND")
    j1 = ComponentIR(
        id="J1", symbol_class="CONNECTOR", value="UART_HDR_1X4", package="HDR-1X4",
        unit=1, position=_p(3400, 3000), rotation=0, mirror=False, confidence=1.0,
        pins=[
            PinIR(number="1", function="VCC", pos=_p(3400 + 80, 3000 + 90), net="VCC", electrical_type="POWER"),
            PinIR(number="2", function="TX", pos=_p(3400 + 80, 3000 + 30), net="MCU_RX", electrical_type="OUTPUT"),
            PinIR(number="3", function="RX", pos=_p(3400 + 80, 3000 - 30), net="MCU_TX", electrical_type="INPUT"),
            PinIR(number="4", function="GND", pos=_p(3400 + 80, 3000 - 90), net="GND", electrical_type="POWER"),
        ]
    )
    vcc1 = _power("VCC1", "VCC", "VCC", 3800, 3600)
    gnd1 = _power("GND1", "GROUND", "GND", 4200, 2200)

    nets = [
        _net("VCC", False, [["VCC1", "1"], ["U1", "7"], ["U1", "20"], ["R1", "1"], ["C3", "1"], ["J1", "1"]], [LabelIR(text="VCC_5V", pos=_p(3800, 3600))]),
        _net("GND", False, [["GND1", "1"], ["U1", "8"], ["U1", "22"], ["SW1", "2"], ["C1", "2"], ["C2", "2"], ["C3", "2"], ["C4", "2"], ["D1", "2"], ["J1", "4"]], [LabelIR(text="GND", pos=_p(4200, 2200))]),
        _net("RESET_NET", False, [["R1", "2"], ["SW1", "1"], ["U1", "1"]], [LabelIR(text="RESET", pos=_p(3750, 3250))]),
        _net("XTAL1_NET", True, [["U1", "9"], ["Y1", "1"], ["C1", "1"]]),
        _net("XTAL2_NET", True, [["U1", "10"], ["Y1", "2"], ["C2", "1"]]),
        _net("AREF_NET", True, [["U1", "21"], ["C4", "1"]]),
        _net("MCU_RX", False, [["U1", "2"], ["J1", "2"]], [LabelIR(text="UART_RX", pos=_p(3500, 3100))]),
        _net("MCU_TX", False, [["U1", "3"], ["J1", "3"]], [LabelIR(text="UART_TX", pos=_p(3500, 2900))]),
        _net("LED_DRIVE", True, [["U1", "19"], ["R2", "1"]]),
        _net("LED_NET", True, [["R2", "2"], ["D1", "1"]]),
    ]
    return DesignIR(
        design=DesignInfo(name="mcu_minimum_system"),
        components=[u1, r1, sw1, y1, c1, c2, c3, c4, r2, d1, j1, vcc1, gnd1],
        nets=nets,
        metadata=DesignMetadata(source="synthetic", mode="vector", confidence=1.0, ocr_confidence=1.0)
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
    "bjt_astable": bjt_astable,
    "h_bridge": h_bridge,
    "diff_amp": diff_amp,
    "bandpass_filter": bandpass_filter,
    "timer_555_astable": timer_555_astable,
    "buck_converter": buck_converter,
    "mcu_minimum_system": mcu_minimum_system,
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

        pdf_path = out_dir / "schematic.pdf"
        png_path = out_dir / "schematic.png"
        render_ir_to_pdf(ir, str(pdf_path))
        render_ir_to_png(ir, str(png_path))

        print(f"[gen] {name}: {len(ir.components)} components, "
              f"{len(ir.nets)} nets -> {out_dir}")


if __name__ == "__main__":
    main()
