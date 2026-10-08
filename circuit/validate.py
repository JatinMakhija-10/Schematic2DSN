"""
circuit/validate.py  --  S9: Validate the IR and compute confidence score.

Checks emitted as coded warnings or errors:
  - UNCONNECTED_PIN: pin with no net
  - SINGLE_PIN_NET: net with only one pin (dangling wire)
  - DUPLICATE_REFDES: same id used twice
  - NO_LIBRARY_MAPPING: symbol_class not in symbol_map.json
  - REFDES_PREFIX_MISMATCH: refdes prefix doesn't match symbol class
  - NET_LABEL_CONFLICT: net has two different labels
  - PIN_ON_TWO_NETS: pin appears in two different nets (snapping bug)
  - NO_PINS_FOUND: component with empty pins list

Confidence formula (documented, not a magic number):
  w_symbol = 0.35 * mean(component.confidence)
  w_ocr    = 0.25 * ocr_confidence
  w_pinconn= 0.25 * fraction_pins_connected
  w_netconn= 0.15 * fraction_nets_with_2plus_pins
  penalty  = 0.05 * min(n_warnings, 10) / 10
  confidence = w_symbol + w_ocr + w_pinconn + w_netconn - penalty
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    DesignIR, ComponentIR, NetIR, WarningIR
)

# Load symbol map for library mapping check
_SYMBOL_MAP_PATH = Path(__file__).parent.parent / "orcad" / "symbol_map.json"


def _load_symbol_map() -> dict:
    with open(_SYMBOL_MAP_PATH) as f:
        return json.load(f)["map"]


def validate(ir: DesignIR) -> Tuple[DesignIR, float]:
    """
    Validate the design IR and return (validated_ir, confidence).

    Adds warnings to ir.warnings in place. Returns confidence score [0,1].
    """
    warnings: List[WarningIR] = list(ir.warnings)
    sym_map = _load_symbol_map()

    # Index: refdes -> component
    refdes_index: Dict[str, List[ComponentIR]] = {}
    for comp in ir.components:
        refdes_index.setdefault(comp.id, []).append(comp)

    # Index: (refdes, pin_num) -> list of net names
    pin_net_index: Dict[Tuple[str, str], List[str]] = {}
    for net in ir.nets:
        for pin_ref in net.pins:
            key = (pin_ref[0], pin_ref[1])
            pin_net_index.setdefault(key, []).append(net.name)

    total_pins = 0
    connected_pins = 0

    for comp in ir.components:
        # NO_LIBRARY_MAPPING
        if comp.symbol_class not in sym_map:
            warnings.append(WarningIR(
                code="NO_LIBRARY_MAPPING",
                detail=f"{comp.id} has class {comp.symbol_class} not in symbol_map.json",
                component=comp.id
            ))

        # DUPLICATE_REFDES
        if len(refdes_index.get(comp.id, [])) > 1:
            warnings.append(WarningIR(
                code="DUPLICATE_REFDES",
                detail=f"Refdes {comp.id} used by {len(refdes_index[comp.id])} components",
                component=comp.id
            ))

        # REFDES_PREFIX_MISMATCH
        import re
        from core.units import CLASS_PREFIX
        prefix_m = re.match(r'^([A-Z]+)', comp.id)
        if prefix_m:
            prefix = prefix_m.group(1)
            valid = CLASS_PREFIX.get(comp.symbol_class, set())
            if valid and prefix not in valid:
                warnings.append(WarningIR(
                    code="REFDES_PREFIX_MISMATCH",
                    detail=f"{comp.id} prefix '{prefix}' not valid for {comp.symbol_class}",
                    component=comp.id
                ))

        # NO_PINS_FOUND
        if not comp.pins:
            warnings.append(WarningIR(
                code="NO_PINS_FOUND",
                detail=f"{comp.id} has no pins",
                component=comp.id
            ))
            continue

        for pin in comp.pins:
            total_pins += 1
            key = (comp.id, pin.number)
            nets_for_pin = pin_net_index.get(key, [])

            # UNCONNECTED_PIN
            if not nets_for_pin and pin.net is None:
                warnings.append(WarningIR(
                    code="UNCONNECTED_PIN",
                    detail=f"{comp.id} pin {pin.number} ({pin.function}) has no net",
                    component=comp.id
                ))
            else:
                connected_pins += 1

            # PIN_ON_TWO_NETS
            if len(nets_for_pin) > 1:
                warnings.append(WarningIR(
                    code="PIN_ON_TWO_NETS",
                    detail=f"{comp.id} pin {pin.number} appears in nets: {nets_for_pin}",
                    component=comp.id
                ))

    # SINGLE_PIN_NET
    for net in ir.nets:
        if len(net.pins) < 2:
            warnings.append(WarningIR(
                code="SINGLE_PIN_NET",
                net=net.name,
                detail=f"Net {net.name} has only {len(net.pins)} pin(s)"
            ))

    # NET_LABEL_CONFLICT: auto-named net with more than one label text
    for net in ir.nets:
        label_texts = list({lbl.text.upper() for lbl in net.labels})
        if len(label_texts) > 1:
            warnings.append(WarningIR(
                code="NET_LABEL_CONFLICT",
                net=net.name,
                detail=f"Net {net.name} has conflicting labels: {label_texts}"
            ))

    ir.warnings = warnings

    # --- Confidence calculation ---
    sym_conf = (
        sum(c.confidence for c in ir.components) / len(ir.components)
        if ir.components else 0.0
    )
    ocr_conf = ir.metadata.ocr_confidence if ir.metadata else 1.0
    pin_conn_frac = connected_pins / total_pins if total_pins > 0 else 0.0
    nets_with_2plus = sum(1 for n in ir.nets if len(n.pins) >= 2)
    net_frac = nets_with_2plus / len(ir.nets) if ir.nets else 0.0

    n_warnings = len([w for w in warnings if w.code not in {
        "SINGLE_PIN_NET"  # not penalized as harshly
    }])

    confidence = (
        0.35 * sym_conf
        + 0.25 * ocr_conf
        + 0.25 * pin_conn_frac
        + 0.15 * net_frac
        - 0.05 * min(n_warnings, 10) / 10
    )
    confidence = max(0.0, min(1.0, confidence))

    if ir.metadata:
        ir.metadata.confidence = confidence

    return ir, confidence
