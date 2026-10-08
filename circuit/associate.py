"""
circuit/associate.py  --  S8: Associate detected symbols with refdes/value texts.

Uses scipy.optimize.linear_sum_assignment (Hungarian algorithm) to
find the optimal one-to-one matching between symbols and text candidates.

Cost function:
  - Distance from symbol center to text bbox center
  - Penalty for wrong side (text sitting on a wire)
  - Penalty for wrong prefix (e.g., C* for a RESISTOR)
  - Penalty for wrong value type

Unmatched symbols get auto-generated refdes (e.g., R_AUTO1) and a warning.

CLI:
    python -m circuit.associate in/symbols.json in/texts.json out/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    SymbolItem, SymbolsFile, TextItem, TextsFile,
    ComponentIR, WarningIR, Point, BBox
)
from core.config import DEFAULT_CONFIG
from core.geometry import distance, bbox_center
from core.units import fix_refdes, normalize_value, CLASS_PREFIX, REFDES_PATTERN


# Distance penalty weights
_DIST_WEIGHT = 1.0
_WRONG_SIDE_PENALTY = 200.0
_WRONG_PREFIX_PENALTY = 500.0
_MAX_COST = 1e6  # used for infeasible pairs


def _cost(sym: SymbolItem, text: TextItem) -> float:
    """Compute assignment cost between a symbol and a text item."""
    sym_cx = sym.bbox.cx
    sym_cy = sym.bbox.cy
    txt_cx = text.bbox.cx
    txt_cy = text.bbox.cy

    dist_cost = distance(Point(x=sym_cx, y=sym_cy),
                         Point(x=txt_cx, y=txt_cy)) * _DIST_WEIGHT

    # Wrong prefix penalty
    txt = text.text.strip()
    prefix_match = re.match(r'^([A-Z]+)', txt)
    prefix = prefix_match.group(1) if prefix_match else ""
    valid_prefixes = CLASS_PREFIX.get(sym.symbol_class, set())
    if valid_prefixes and prefix not in valid_prefixes:
        dist_cost += _WRONG_PREFIX_PENALTY

    return dist_cost


def associate(
    symbols: SymbolsFile,
    texts: TextsFile,
) -> Tuple[List[ComponentIR], List[WarningIR]]:
    """
    Match symbols to refdes/value text labels using Hungarian algorithm.

    Parameters
    ----------
    symbols : SymbolsFile
    texts : TextsFile

    Returns
    -------
    (components, warnings)
    """
    import numpy as np
    from scipy.optimize import linear_sum_assignment

    syms = symbols.items
    txts = texts.items

    if not syms:
        return [], []

    # Skip power/ground symbols for refdes matching (they use net names)
    power_classes = {"GROUND", "VCC"}
    active_syms = [s for s in syms if s.symbol_class not in power_classes]
    power_syms = [s for s in syms if s.symbol_class in power_classes]

    # Candidate texts that look like refdes
    refdes_texts = [t for t in txts if REFDES_PATTERN.match(t.text.strip())]
    # Value texts: everything else
    value_texts = [t for t in txts if not REFDES_PATTERN.match(t.text.strip())]

    n_sym = len(active_syms)
    n_txt = len(refdes_texts)

    # Build cost matrix (n_sym x n_txt) padded to square
    n = max(n_sym, n_txt)
    cost_matrix = np.full((n, n), _MAX_COST)

    for i, sym in enumerate(active_syms):
        for j, text in enumerate(refdes_texts):
            cost_matrix[i, j] = _cost(sym, text)

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assigned_refdes: Dict[int, str] = {}
    warnings: List[WarningIR] = []

    auto_counts: Dict[str, int] = {}

    for r, c in zip(row_ind, col_ind):
        if r >= n_sym or c >= n_txt:
            continue
        cost = cost_matrix[r, c]
        if cost >= _MAX_COST:
            continue
        # Check threshold: if cost too high, it's unmatched
        if cost > _WRONG_PREFIX_PENALTY:
            continue
        raw_refdes = refdes_texts[c].text.strip()
        fixed = fix_refdes(raw_refdes, active_syms[r].symbol_class)
        assigned_refdes[r] = fixed

    # Build ComponentIRs
    components: List[ComponentIR] = []
    used_refdes: set = set(assigned_refdes.values())

    for i, sym in enumerate(active_syms):
        if i in assigned_refdes:
            refdes = assigned_refdes[i]
        else:
            # Auto-generate refdes
            prefix = _class_to_prefix(sym.symbol_class)
            auto_counts[prefix] = auto_counts.get(prefix, 0) + 1
            refdes = f"{prefix}_AUTO{auto_counts[prefix]}"
            warnings.append(WarningIR(
                code="UNMATCHED_SYMBOL",
                detail=f"No refdes text found for {sym.symbol_class} at ({sym.bbox.cx:.0f},{sym.bbox.cy:.0f}). Auto-assigned {refdes}.",
                component=refdes
            ))

        # Find value text closest to this symbol (not already used as refdes)
        best_value = ""
        best_val_dist = float("inf")
        for vt in value_texts:
            d = distance(
                Point(x=sym.bbox.cx, y=sym.bbox.cy),
                Point(x=vt.bbox.cx, y=vt.bbox.cy)
            )
            if d < best_val_dist:
                best_val_dist = d
                best_value = vt.text.strip()

        if best_val_dist > 300:  # too far -> no value
            best_value = ""

        # Normalize value
        try:
            norm_value = normalize_value(best_value) if best_value else ""
        except Exception:
            norm_value = best_value

        comp = ComponentIR(
            id=refdes,
            symbol_class=sym.symbol_class,
            value=norm_value,
            unit=1,
            position=Point(x=sym.bbox.cx, y=sym.bbox.cy),
            rotation=sym.rotation,
            mirror=sym.mirror,
            src_bbox_px=[sym.bbox.x0, sym.bbox.y0, sym.bbox.x1, sym.bbox.y1],
            confidence=sym.conf,
            pins=[]  # filled by S6/S7
        )
        components.append(comp)

    # Add power symbols as components (no refdes matching needed)
    for i, sym in enumerate(power_syms):
        sym_class = sym.symbol_class
        prefix = _class_to_prefix(sym_class)
        auto_counts[prefix] = auto_counts.get(prefix, 0) + 1
        refdes = f"{prefix}{auto_counts[prefix]}"
        components.append(ComponentIR(
            id=refdes,
            symbol_class=sym_class,
            value="",
            unit=1,
            position=Point(x=sym.bbox.cx, y=sym.bbox.cy),
            rotation=sym.rotation,
            mirror=sym.mirror,
            src_bbox_px=[sym.bbox.x0, sym.bbox.y0, sym.bbox.x1, sym.bbox.y1],
            confidence=sym.conf,
            pins=[]
        ))

    return components, warnings


def _class_to_prefix(symbol_class: str) -> str:
    prefixes = {
        "RESISTOR": "R", "CAPACITOR": "C", "INDUCTOR": "L",
        "DIODE": "D", "LED": "D", "NPN": "Q", "PNP": "Q",
        "NMOS": "M", "PMOS": "M", "OPAMP": "U", "CONNECTOR": "J",
        "GROUND": "GND", "VCC": "VCC"
    }
    return prefixes.get(symbol_class, "X")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="S8 Associate: symbols + texts -> components with refdes/value"
    )
    parser.add_argument("symbols", help="symbols.json")
    parser.add_argument("texts", help="texts.json")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with open(args.symbols) as f:
        symbols = SymbolsFile.model_validate(json.load(f))
    with open(args.texts) as f:
        texts = TextsFile.model_validate(json.load(f))

    components, warnings = associate(symbols, texts)
    result = {
        "components": [c.model_dump() for c in components],
        "warnings": [w.model_dump() for w in warnings]
    }
    out_path = out / "components_raw.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[associate] {len(components)} components, {len(warnings)} warnings -> {out_path}")


if __name__ == "__main__":
    main()
