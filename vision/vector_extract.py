"""
vision/vector_extract.py  --  S2+S4 vector path: extract text and wires from PDF.

When the PDF is vector (page.meta.json mode == "vector"), this module replaces
both the OCR pass (S2) and the raster wire detection (S4) with exact data from
PyMuPDF's page.get_text("dict") and page.get_drawings().

Outputs:
  - texts.json   (TextsFile)
  - wires.json   (WiresFile)
  - out/debug/vector_text.png
  - out/debug/vector_wires.png

CLI:
    python -m vision.vector_extract in/page.png in/page.meta.json out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    TextItem, TextsFile, BBox, Point,
    WireSegment, WiresFile, PageMeta
)
from core.config import DEFAULT_CONFIG

# Counter for stable IDs
_wire_counter = 0


def _next_wire_id() -> str:
    global _wire_counter
    _wire_counter += 1
    return f"W_{_wire_counter:04d}"


def _reset_counter() -> None:
    global _wire_counter
    _wire_counter = 0


# ---------------------------------------------------------------------------
# Text extraction from PDF vector data
# ---------------------------------------------------------------------------

def extract_vector_text(pdf_path: str) -> TextsFile:
    """
    Extract text spans from a vector PDF using PyMuPDF get_text("dict").
    Returns a TextsFile with one TextItem per span.
    """
    import fitz

    doc = fitz.open(pdf_path)
    page = doc[0]
    blocks = page.get_text("dict")["blocks"]
    items: List[TextItem] = []

    for block in blocks:
        if block.get("type") != 0:  # type 0 = text
            continue
        for line in block.get("lines", []):
            angle = 0.0
            # Line direction vector -> angle in degrees
            dir_vec = line.get("dir", (1, 0))
            import math
            angle = math.degrees(math.atan2(-dir_vec[1], dir_vec[0]))
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue
                bbox_raw = span.get("bbox", (0, 0, 0, 0))
                bbox = BBox(
                    x0=bbox_raw[0], y0=bbox_raw[1],
                    x1=bbox_raw[2], y1=bbox_raw[3]
                )
                items.append(TextItem(
                    text=text,
                    bbox=bbox,
                    angle=round(angle, 1),
                    conf=1.0,
                    source="vector"
                ))

    return TextsFile(items=items)


# ---------------------------------------------------------------------------
# Wire extraction from PDF vector data
# ---------------------------------------------------------------------------

def _is_horizontal(p0: Tuple[float, float], p1: Tuple[float, float],
                   tol_deg: float = 5.0) -> bool:
    import math
    if abs(p1[0] - p0[0]) < 1e-6:
        return False
    angle = abs(math.degrees(math.atan2(abs(p1[1] - p0[1]), abs(p1[0] - p0[0]))))
    return angle <= tol_deg


def _is_vertical(p0: Tuple[float, float], p1: Tuple[float, float],
                 tol_deg: float = 5.0) -> bool:
    import math
    if abs(p1[1] - p0[1]) < 1e-6:
        return False
    angle = abs(math.degrees(math.atan2(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))))
    return angle <= tol_deg


def _snap_orthogonal(p0: Tuple[float, float],
                     p1: Tuple[float, float]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Snap a nearly-orthogonal segment to exactly H or V."""
    dx = abs(p1[0] - p0[0])
    dy = abs(p1[1] - p0[1])
    if dx >= dy:
        # Horizontal: average y
        y = (p0[1] + p1[1]) / 2
        return (p0[0], y), (p1[0], y)
    else:
        # Vertical: average x
        x = (p0[0] + p1[0]) / 2
        return (x, p0[1]), (x, p1[1])


def _merge_collinear(segments: List[WireSegment],
                     lateral_tol: float = 2.0,
                     gap_tol: float = 3.0) -> List[WireSegment]:
    """
    Merge collinear touching/overlapping wire segments.
    Groups by (is_horizontal, fixed_coord) then merges along the free axis.
    """
    import math

    h_groups: dict = {}  # y_rounded -> list of (x0, x1)
    v_groups: dict = {}  # x_rounded -> list of (y0, y1)

    for seg in segments:
        if abs(seg.p0.y - seg.p1.y) < lateral_tol:
            # Horizontal
            y_key = round((seg.p0.y + seg.p1.y) / 2 / lateral_tol) * lateral_tol
            x0, x1 = min(seg.p0.x, seg.p1.x), max(seg.p0.x, seg.p1.x)
            h_groups.setdefault(y_key, []).append((x0, x1))
        elif abs(seg.p0.x - seg.p1.x) < lateral_tol:
            # Vertical
            x_key = round((seg.p0.x + seg.p1.x) / 2 / lateral_tol) * lateral_tol
            y0, y1 = min(seg.p0.y, seg.p1.y), max(seg.p0.y, seg.p1.y)
            v_groups.setdefault(x_key, []).append((y0, y1))

    merged: List[WireSegment] = []

    for y_key, segs in h_groups.items():
        segs.sort(key=lambda s: s[0])
        current_x0, current_x1 = segs[0]
        for x0, x1 in segs[1:]:
            if x0 <= current_x1 + gap_tol:
                current_x1 = max(current_x1, x1)
            else:
                merged.append(WireSegment(
                    id=_next_wire_id(),
                    p0=Point(x=current_x0, y=y_key),
                    p1=Point(x=current_x1, y=y_key)
                ))
                current_x0, current_x1 = x0, x1
        merged.append(WireSegment(
            id=_next_wire_id(),
            p0=Point(x=current_x0, y=y_key),
            p1=Point(x=current_x1, y=y_key)
        ))

    for x_key, segs in v_groups.items():
        segs.sort(key=lambda s: s[0])
        current_y0, current_y1 = segs[0]
        for y0, y1 in segs[1:]:
            if y0 <= current_y1 + gap_tol:
                current_y1 = max(current_y1, y1)
            else:
                merged.append(WireSegment(
                    id=_next_wire_id(),
                    p0=Point(x=x_key, y=current_y0),
                    p1=Point(x=x_key, y=current_y1)
                ))
                current_y0, current_y1 = y0, y1
        merged.append(WireSegment(
            id=_next_wire_id(),
            p0=Point(x=x_key, y=current_y0),
            p1=Point(x=x_key, y=current_y1)
        ))

    return merged


def extract_vector_wires(pdf_path: str, symbol_bboxes: List[BBox] | None = None) -> WiresFile:
    """
    Extract horizontal/vertical wire segments from PDF vector drawings.

    Parameters
    ----------
    pdf_path : str
        Path to the source PDF.
    symbol_bboxes : list of BBox, optional
        Component bounding boxes to exclude segments inside.

    Returns
    -------
    WiresFile
    """
    import fitz

    _reset_counter()
    cfg = DEFAULT_CONFIG.wire
    doc = fitz.open(pdf_path)
    page = doc[0]
    drawings = page.get_drawings()

    raw_segments: List[WireSegment] = []

    for drawing in drawings:
        for item in drawing.get("items", []):
            if item[0] != "l":  # 'l' = line segment
                continue
            p0_raw, p1_raw = item[1], item[2]
            p0 = (p0_raw.x, p0_raw.y)
            p1 = (p1_raw.x, p1_raw.y)

            # Skip zero-length
            dx = abs(p1[0] - p0[0])
            dy = abs(p1[1] - p0[1])
            if dx < 1e-3 and dy < 1e-3:
                continue

            # Only keep orthogonal segments
            if not (_is_horizontal(p0, p1, cfg.snap_angle_degrees) or
                    _is_vertical(p0, p1, cfg.snap_angle_degrees)):
                continue

            sp0, sp1 = _snap_orthogonal(p0, p1)
            seg = WireSegment(
                id=_next_wire_id(),
                p0=Point(x=round(sp0[0], 1), y=round(sp0[1], 1)),
                p1=Point(x=round(sp1[0], 1), y=round(sp1[1], 1))
            )

            # Skip segments inside symbol bboxes
            if symbol_bboxes:
                cx = (seg.p0.x + seg.p1.x) / 2
                cy = (seg.p0.y + seg.p1.y) / 2
                center = Point(x=cx, y=cy)
                if any(bb.contains(center) for bb in symbol_bboxes):
                    continue

            raw_segments.append(seg)

    merged = _merge_collinear(
        raw_segments,
        lateral_tol=cfg.merge_lateral_px,
        gap_tol=cfg.merge_gap_px
    )

    # Collect unique endpoints
    endpoint_set: set = set()
    for seg in merged:
        endpoint_set.add((seg.p0.x, seg.p0.y))
        endpoint_set.add((seg.p1.x, seg.p1.y))
    endpoints = [Point(x=x, y=y) for x, y in sorted(endpoint_set)]

    return WiresFile(segments=merged, endpoints=endpoints)


# ---------------------------------------------------------------------------
# Debug overlay
# ---------------------------------------------------------------------------

def draw_text_overlay(img_path: str, texts: TextsFile, out_path: str) -> None:
    """Draw bounding boxes and text labels on the page image."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return

    img = cv2.imread(img_path)
    if img is None:
        return

    for item in texts.items:
        x0, y0, x1, y1 = (int(item.bbox.x0), int(item.bbox.y0),
                           int(item.bbox.x1), int(item.bbox.y1))
        cv2.rectangle(img, (x0, y0), (x1, y1), (0, 200, 0), 1)
        cv2.putText(img, item.text[:20], (x0, max(y0 - 2, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 150, 0), 1)

    cv2.imwrite(out_path, img)


def draw_wire_overlay(img_path: str, wires: WiresFile, out_path: str) -> None:
    """Draw wire segments as blue lines on the page image."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return

    img = cv2.imread(img_path)
    if img is None:
        return

    for seg in wires.segments:
        pt0 = (int(seg.p0.x), int(seg.p0.y))
        pt1 = (int(seg.p1.x), int(seg.p1.y))
        cv2.line(img, pt0, pt1, (255, 80, 0), 2)

    for ep in wires.endpoints:
        cv2.circle(img, (int(ep.x), int(ep.y)), 3, (0, 0, 255), -1)

    cv2.imwrite(out_path, img)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="S2+S4 vector extract: PDF -> texts.json + wires.json"
    )
    parser.add_argument("pdf", help="Source PDF file")
    parser.add_argument("meta", help="page.meta.json from ingest stage")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "debug").mkdir(exist_ok=True)

    with open(args.meta) as f:
        meta = PageMeta.model_validate(json.load(f))

    if meta.mode != "vector":
        print(f"[vector_extract] mode={meta.mode}; skipping (not vector PDF)")
        sys.exit(0)

    print("[vector_extract] Extracting text...")
    texts = extract_vector_text(args.pdf)
    texts_path = out / "texts.json"
    texts_path.write_text(texts.model_dump_json(indent=2), encoding="utf-8")
    print(f"[vector_extract] {len(texts.items)} text spans -> {texts_path}")

    print("[vector_extract] Extracting wires...")
    wires = extract_vector_wires(args.pdf)
    wires_path = out / "wires.json"
    wires_path.write_text(wires.model_dump_json(indent=2), encoding="utf-8")
    print(f"[vector_extract] {len(wires.segments)} wire segments -> {wires_path}")

    img_path = str(out / "page.png")
    draw_text_overlay(img_path, texts, str(out / "debug" / "vector_text.png"))
    draw_wire_overlay(img_path, wires, str(out / "debug" / "vector_wires.png"))
    print("[vector_extract] Debug overlays written.")


if __name__ == "__main__":
    main()
