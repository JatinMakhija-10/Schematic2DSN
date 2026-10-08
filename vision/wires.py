"""
vision/wires.py  --  S4 raster path: wire segment detection from image.

Pipeline:
  1. Remove component and text regions (dilate bboxes by N px)
  2. Skeletonize
  3. Probabilistic Hough (H/V only)
  4. Merge collinear segments (lateral + gap tolerance)
  5. Split at T-intersections

Outputs:
  - wires.json  (WiresFile)
  - out/debug/wires.png

CLI:
    python -m vision.wires in/page.png in/symbols.json in/texts.json out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    WireSegment, WiresFile, BBox, Point,
    SymbolsFile, TextsFile
)
from core.config import DEFAULT_CONFIG

_wire_counter = 0


def _next_wire_id() -> str:
    global _wire_counter
    _wire_counter += 1
    return f"W_{_wire_counter:04d}"


def _reset_wire_counter() -> None:
    global _wire_counter
    _wire_counter = 0


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def detect_wires(
    img_path: str,
    symbols: Optional[SymbolsFile] = None,
    texts: Optional[TextsFile] = None,
) -> WiresFile:
    """
    Detect orthogonal wire segments in a raster schematic image.

    Parameters
    ----------
    img_path : str
        Path to the page image (grayscale or RGB).
    symbols : SymbolsFile, optional
        Component bounding boxes to mask out.
    texts : TextsFile, optional
        Text bounding boxes to mask out.

    Returns
    -------
    WiresFile
    """
    import cv2
    import numpy as np
    from skimage.morphology import skeletonize

    _reset_wire_counter()
    cfg = DEFAULT_CONFIG.wire

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Cannot read: {img_path}")

    h, w = img.shape

    # Binarize
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Estimate line thickness (median of non-zero widths of thin structures)
    line_thickness = _estimate_line_thickness(binary)

    # Mask component and text regions
    mask = binary.copy()
    dilate_px = cfg.bbox_dilate_px

    if symbols:
        for sym in symbols.items:
            x0 = max(0, int(sym.bbox.x0) - dilate_px)
            y0 = max(0, int(sym.bbox.y0) - dilate_px)
            x1 = min(w, int(sym.bbox.x1) + dilate_px)
            y1 = min(h, int(sym.bbox.y1) + dilate_px)
            mask[y0:y1, x0:x1] = 0

    if texts:
        for text in texts.items:
            x0 = max(0, int(text.bbox.x0) - dilate_px)
            y0 = max(0, int(text.bbox.y0) - dilate_px)
            x1 = min(w, int(text.bbox.x1) + dilate_px)
            y1 = min(h, int(text.bbox.y1) + dilate_px)
            mask[y0:y1, x0:x1] = 0

    # Skeletonize
    skel = skeletonize(mask > 0).astype(np.uint8) * 255

    # Probabilistic Hough
    min_length = max(10, int(cfg.hough_min_length_factor * line_thickness * 8))
    lines = cv2.HoughLinesP(
        skel,
        rho=1,
        theta=3.14159 / 180,
        threshold=cfg.hough_threshold,
        minLineLength=min_length,
        maxLineGap=int(cfg.merge_gap_px)
    )

    raw_segments: List[WireSegment] = []
    if lines is not None:
        snap_tol = cfg.snap_angle_degrees
        for line in lines:
            x0, y0, x1, y1 = line[0]
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            import math
            if dx + dy < 1:
                continue
            angle = math.degrees(math.atan2(dy, dx))
            if angle > 45:  # closer to vertical
                if angle < 90 - snap_tol:
                    continue  # diagonal - skip
                # Snap to vertical
                xm = (x0 + x1) // 2
                raw_segments.append(WireSegment(
                    id=_next_wire_id(),
                    p0=Point(x=float(xm), y=float(y0)),
                    p1=Point(x=float(xm), y=float(y1))
                ))
            else:  # closer to horizontal
                if angle > snap_tol:
                    continue  # diagonal - skip
                # Snap to horizontal
                ym = (y0 + y1) // 2
                raw_segments.append(WireSegment(
                    id=_next_wire_id(),
                    p0=Point(x=float(x0), y=float(ym)),
                    p1=Point(x=float(x1), y=float(ym))
                ))

    # Merge collinear segments
    merged = _merge_collinear(raw_segments, cfg.merge_lateral_px, cfg.merge_gap_px)

    # Split at T-intersections
    split = _split_at_t_intersections(merged)

    # Unique endpoints
    endpoint_set: set = set()
    for seg in split:
        endpoint_set.add((seg.p0.x, seg.p0.y))
        endpoint_set.add((seg.p1.x, seg.p1.y))
    endpoints = [Point(x=x, y=y) for x, y in sorted(endpoint_set)]

    return WiresFile(segments=split, endpoints=endpoints)


def _estimate_line_thickness(binary) -> float:
    """Estimate median wire line thickness from the binary image."""
    import cv2
    import numpy as np

    # Use distance transform: max value inside each wire gives half-thickness
    dist = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    vals = dist[dist > 0]
    if len(vals) == 0:
        return 1.0
    return float(np.median(vals)) * 2


def _merge_collinear(
    segments: List[WireSegment],
    lateral_tol: float,
    gap_tol: float
) -> List[WireSegment]:
    """
    Merge segments that are collinear and close/touching.
    Groups horizontal by y, vertical by x.
    """
    h_groups: dict = {}
    v_groups: dict = {}

    for seg in segments:
        if abs(seg.p0.y - seg.p1.y) < lateral_tol:
            y_key = round((seg.p0.y + seg.p1.y) / 2 / lateral_tol) * lateral_tol
            x0, x1 = min(seg.p0.x, seg.p1.x), max(seg.p0.x, seg.p1.x)
            h_groups.setdefault(y_key, []).append((x0, x1))
        else:
            x_key = round((seg.p0.x + seg.p1.x) / 2 / lateral_tol) * lateral_tol
            y0, y1 = min(seg.p0.y, seg.p1.y), max(seg.p0.y, seg.p1.y)
            v_groups.setdefault(x_key, []).append((y0, y1))

    merged: List[WireSegment] = []

    for y_key, segs in h_groups.items():
        segs.sort()
        cx0, cx1 = segs[0]
        for x0, x1 in segs[1:]:
            if x0 <= cx1 + gap_tol:
                cx1 = max(cx1, x1)
            else:
                merged.append(WireSegment(id=_next_wire_id(),
                                          p0=Point(x=cx0, y=y_key),
                                          p1=Point(x=cx1, y=y_key)))
                cx0, cx1 = x0, x1
        merged.append(WireSegment(id=_next_wire_id(),
                                  p0=Point(x=cx0, y=y_key),
                                  p1=Point(x=cx1, y=y_key)))

    for x_key, segs in v_groups.items():
        segs.sort()
        cy0, cy1 = segs[0]
        for y0, y1 in segs[1:]:
            if y0 <= cy1 + gap_tol:
                cy1 = max(cy1, y1)
            else:
                merged.append(WireSegment(id=_next_wire_id(),
                                          p0=Point(x=x_key, y=cy0),
                                          p1=Point(x=x_key, y=cy1)))
                cy0, cy1 = y0, y1
        merged.append(WireSegment(id=_next_wire_id(),
                                  p0=Point(x=x_key, y=cy0),
                                  p1=Point(x=x_key, y=cy1)))

    return merged


def _split_at_t_intersections(segments: List[WireSegment]) -> List[WireSegment]:
    """
    Split segments where another segment's endpoint lies on their interior.
    This creates proper T-junction topology.
    """
    import math

    def pt_on_seg_interior(p: Tuple[float, float],
                            s0: Tuple[float, float],
                            s1: Tuple[float, float],
                            tol: float = 3.0) -> bool:
        """Return True if p lies strictly inside (not at endpoints of) segment s0-s1."""
        # Axis-aligned only
        if abs(s0[1] - s1[1]) < 1:  # horizontal
            if abs(p[1] - s0[1]) > tol:
                return False
            mn, mx = min(s0[0], s1[0]), max(s0[0], s1[0])
            return mn + tol < p[0] < mx - tol
        else:  # vertical
            if abs(p[0] - s0[0]) > tol:
                return False
            mn, mx = min(s0[1], s1[1]), max(s0[1], s1[1])
            return mn + tol < p[1] < mx - tol

    # Collect all endpoints
    endpoints = []
    for seg in segments:
        endpoints.append((seg.p0.x, seg.p0.y))
        endpoints.append((seg.p1.x, seg.p1.y))

    result: List[WireSegment] = []
    for seg in segments:
        s0 = (seg.p0.x, seg.p0.y)
        s1 = (seg.p1.x, seg.p1.y)
        split_points = []
        for ep in endpoints:
            if pt_on_seg_interior(ep, s0, s1):
                split_points.append(ep)

        if not split_points:
            result.append(seg)
            continue

        # Sort split points along the segment
        is_h = abs(s0[1] - s1[1]) < 1
        key_fn = (lambda p: p[0]) if is_h else (lambda p: p[1])
        split_points.sort(key=key_fn)

        prev = s0
        for sp in split_points:
            result.append(WireSegment(
                id=_next_wire_id(),
                p0=Point(x=prev[0], y=prev[1]),
                p1=Point(x=sp[0], y=sp[1])
            ))
            prev = sp
        result.append(WireSegment(
            id=_next_wire_id(),
            p0=Point(x=prev[0], y=prev[1]),
            p1=Point(x=s1[0], y=s1[1])
        ))

    return result


# ---------------------------------------------------------------------------
# Debug overlay
# ---------------------------------------------------------------------------

def draw_wire_overlay(img_path: str, wires: WiresFile, out_path: str) -> None:
    try:
        import cv2
    except ImportError:
        return
    img = cv2.imread(img_path)
    if img is None:
        return
    for seg in wires.segments:
        cv2.line(img,
                 (int(seg.p0.x), int(seg.p0.y)),
                 (int(seg.p1.x), int(seg.p1.y)),
                 (255, 100, 0), 2)
    for ep in wires.endpoints:
        cv2.circle(img, (int(ep.x), int(ep.y)), 3, (0, 0, 255), -1)
    cv2.imwrite(out_path, img)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="S4 Wire detection (raster): page.png -> wires.json"
    )
    parser.add_argument("img", help="Input page.png")
    parser.add_argument("symbols", help="symbols.json")
    parser.add_argument("texts", help="texts.json")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "debug").mkdir(exist_ok=True)

    with open(args.symbols) as f:
        symbols = SymbolsFile.model_validate(json.load(f))
    with open(args.texts) as f:
        texts = TextsFile.model_validate(json.load(f))

    wires = detect_wires(args.img, symbols, texts)
    wires_path = out / "wires.json"
    wires_path.write_text(wires.model_dump_json(indent=2), encoding="utf-8")
    print(f"[wires] {len(wires.segments)} segments -> {wires_path}")

    draw_wire_overlay(args.img, wires, str(out / "debug" / "wires.png"))
    print("[wires] Debug overlay written.")


if __name__ == "__main__":
    main()
