"""
circuit/confidence.py  --  Formalized confidence score calculator.

Formula:
  w_symbol  = 0.35 * mean(component.confidence)
  w_ocr     = 0.25 * ocr_confidence
  w_pinconn = 0.25 * fraction_pins_connected
  w_netconn = 0.15 * fraction_nets_with_2plus_pins
  penalty   = 0.05 * min(n_critical_warnings, 10) / 10
  confidence = w_symbol + w_ocr + w_pinconn + w_netconn - penalty
"""
from __future__ import annotations

from typing import List
from core.models import DesignIR, WarningIR


def compute_design_confidence(ir: DesignIR) -> float:
    """Compute overall confidence score [0.0, 1.0] for the reconstructed IR."""
    if not ir.components:
        return 0.0

    sym_conf = sum(c.confidence for c in ir.components) / len(ir.components)
    ocr_conf = ir.metadata.ocr_confidence if ir.metadata else 1.0

    total_pins = 0
    connected_pins = 0
    for comp in ir.components:
        for pin in comp.pins:
            total_pins += 1
            if pin.net is not None:
                connected_pins += 1

    pin_conn_frac = connected_pins / total_pins if total_pins > 0 else 0.0
    nets_with_2plus = sum(1 for n in ir.nets if len(n.pins) >= 2)
    net_frac = nets_with_2plus / len(ir.nets) if ir.nets else 0.0

    # Critical warnings penalty
    critical_codes = {
        "UNCONNECTED_PIN", "DUPLICATE_REFDES", "PIN_ON_TWO_NETS",
        "NO_LIBRARY_MAPPING", "NET_LABEL_CONFLICT"
    }
    critical_warnings = [w for w in ir.warnings if w.code in critical_codes]
    penalty = 0.05 * min(len(critical_warnings), 10) / 10.0

    score = (
        0.35 * sym_conf
        + 0.25 * ocr_conf
        + 0.25 * pin_conn_frac
        + 0.15 * net_frac
        - penalty
    )
    return max(0.0, min(1.0, score))
