"""
vision/pins.py  --  S6: Component pin position computation.

Pin positions come from the library contract (orcad/symbols.json),
NOT from image analysis alone. We compute expected pin ends from
(body bbox, rotation, mirror) and snap to the nearest wire endpoint.

Outputs:
  - pins.json (inline in design.json, not a separate file)

This module is called by circuit/graph.py to build pin attachment points.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import SymbolItem, WiresFile, PinIR, Point, BBox
from core.config import DEFAULT_CONFIG
from core.geometry import distance


# Load the library contract once
_SYMBOLS_JSON_PATH = Path(__file__).parent.parent / "orcad" / "symbols.json"
_LIBRARY_CONTRACT: Optional[dict] = None


def _load_library() -> dict:
    global _LIBRARY_CONTRACT
    if _LIBRARY_CONTRACT is None:
        with open(_SYMBOLS_JSON_PATH) as f:
            _LIBRARY_CONTRACT = json.load(f)["symbols"]
    return _LIBRARY_CONTRACT


def _offset_key(rotation: int, mirror: bool) -> str:
    return f"rot{rotation}_mirror_{'true' if mirror else 'false'}"


def compute_pin_positions(
    symbol: SymbolItem,
    scale_px_per_mil: float,
) -> List[Tuple[str, str, Point]]:
    """
    Compute expected pin endpoint positions in pixel coordinates
    for a detected symbol.

    Parameters
    ----------
    symbol : SymbolItem
        The detected symbol with bbox, rotation, mirror.
    scale_px_per_mil : float
        How many pixels equal one mil (from CoordTransform).

    Returns
    -------
    List of (pin_number, pin_function, Point_in_pixels)
    """
    lib = _load_library()
    sym_data = lib.get(symbol.symbol_class)
    if sym_data is None:
        return []

    offsets_map = sym_data.get("pin_offsets", {})
    key = _offset_key(symbol.rotation, symbol.mirror)
    offsets = offsets_map.get(key, {})

    cx = symbol.bbox.cx
    cy = symbol.bbox.cy

    pins = sym_data.get("pins", [])
    result = []
    for pin in pins:
        num = pin["number"]
        func = pin["function"]
        off = offsets.get(num, {"dx": 0, "dy": 0})
        # Convert offset from mils to pixels
        px = cx + off["dx"] * scale_px_per_mil
        # Note: in image coords, positive dy is down; in library contract
        # dy is in Capture coords (up positive), so flip y
        py = cy - off["dy"] * scale_px_per_mil
        result.append((num, func, Point(x=px, y=py)))

    return result


def snap_pins_to_wires(
    pin_points: List[Tuple[str, str, Point]],
    wires: WiresFile,
    tolerance_px: float,
) -> List[PinIR]:
    """
    Snap each computed pin position to the nearest wire endpoint within tolerance.
    If no endpoint is found, the pin is flagged (net=None -> UNCONNECTED_PIN).

    Parameters
    ----------
    pin_points : list of (number, function, Point)
    wires : WiresFile
    tolerance_px : float

    Returns
    -------
    List[PinIR]  -- positions remain in pixel coords (graph.py will convert)
    """
    pins: List[PinIR] = []
    for num, func, expected_pos in pin_points:
        best_dist = float("inf")
        best_pt = expected_pos
        for ep in wires.endpoints:
            d = distance(expected_pos, ep)
            if d < best_dist:
                best_dist = d
                best_pt = ep
        if best_dist <= tolerance_px:
            pins.append(PinIR(number=num, function=func, pos=best_pt, net=None))
        else:
            # UNCONNECTED_PIN: keep expected position, no snap
            pins.append(PinIR(number=num, function=func, pos=expected_pos, net=None))
    return pins
