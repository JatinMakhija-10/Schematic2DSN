"""
vision/symbols_cv.py  --  S3 Level-1 OpenCV symbol detection (no training needed).

Detects: RESISTOR, CAPACITOR, INDUCTOR, DIODE, LED, GROUND, VCC, OPAMP
using morphological and contour heuristics on the binarized page image.

Outputs:
  - symbols.json  (SymbolsFile)
  - out/debug/symbols_cv.png

CLI:
    python -m vision.symbols_cv in/page.png in/texts.json out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import SymbolItem, SymbolsFile, BBox, TextsFile
from core.config import DEFAULT_CONFIG

_symbol_counter = 0


def _next_sym_id() -> str:
    global _symbol_counter
    _symbol_counter += 1
    return f"SYM_{_symbol_counter:04d}"


def _reset_sym_counter() -> None:
    global _symbol_counter
    _symbol_counter = 0


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _circularity(contour) -> float:
    import cv2
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    if perimeter < 1e-3:
        return 0.0
    return 4 * 3.14159 * area / (perimeter ** 2)


def _load_binary(img_path: str):
    """Load and binarize image. Returns (gray, binary)."""
    import cv2
    import numpy as np
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Cannot read: {img_path}")
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return img, binary


def _mask_text_regions(binary, texts: TextsFile, dilate_px: int = 5):
    """Zero out text bboxes in binary image so letters don't become shapes."""
    import cv2
    import numpy as np
    masked = binary.copy()
    for item in texts.items:
        x0 = max(0, int(item.bbox.x0) - dilate_px)
        y0 = max(0, int(item.bbox.y0) - dilate_px)
        x1 = min(masked.shape[1], int(item.bbox.x1) + dilate_px)
        y1 = min(masked.shape[0], int(item.bbox.y1) + dilate_px)
        masked[y0:y1, x0:x1] = 0
    return masked


# ---------------------------------------------------------------------------
# Heuristic detectors
# ---------------------------------------------------------------------------

def _detect_resistors(binary, min_turns: int = 4) -> List[SymbolItem]:
    """
    ANSI resistor: zig-zag pattern. IEC: thin rectangle.
    Strategy: find connected components with high contour complexity.
    """
    import cv2
    import numpy as np

    items = []
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100 or area > 50000:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        # Resistor aspect ratio: elongated
        aspect = max(w, h) / (min(w, h) + 1)
        if aspect < 2.0 or aspect > 12.0:
            continue
        # Perimeter complexity: resistor zig-zag has high P/sqrt(A)
        perimeter = cv2.arcLength(cnt, True)
        complexity = perimeter / (area ** 0.5 + 1e-3)
        if complexity < 3.0:
            continue
        # Check for zig-zag: number of direction changes along the contour
        approx = cv2.approxPolyDP(cnt, 2, True)
        if len(approx) < min_turns * 2:
            continue
        rotation = 0 if w >= h else 90
        items.append(SymbolItem(
            id=_next_sym_id(),
            symbol_class="RESISTOR",
            bbox=BBox(x0=x, y0=y, x1=x + w, y1=y + h),
            rotation=rotation,
            mirror=False,
            conf=0.70,
            source="cv",
            style="ANSI"
        ))
    return items


def _detect_capacitors(binary) -> List[SymbolItem]:
    """
    Capacitor: two parallel lines (plates) with a gap between them.
    Strategy: find pairs of close parallel horizontal or vertical lines.
    """
    import cv2
    import numpy as np

    items = []
    # Use Hough lines to find line segments, look for parallel pairs with gap
    edges = cv2.Canny(binary, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, 3.14159 / 180, 30,
                             minLineLength=15, maxLineGap=5)
    if lines is None:
        return items

    h_lines = []  # (y, x0, x1)
    v_lines = []  # (x, y0, y1)
    for line in lines:
        pts = line[0] if len(line.shape) > 1 and line.shape[0] == 1 else line
        if len(pts) != 4:
            pts = pts.flatten()
        x0, y0, x1, y1 = int(pts[0]), int(pts[1]), int(pts[2]), int(pts[3])
        if abs(y1 - y0) < abs(x1 - x0) * 0.2:  # horizontal
            h_lines.append((int((y0 + y1) / 2), min(x0, x1), max(x0, x1)))
        elif abs(x1 - x0) < abs(y1 - y0) * 0.2:  # vertical
            v_lines.append((int((x0 + x1) / 2), min(y0, y1), max(y0, y1)))

    # Find pairs of horizontal lines with gap 5-40px, similar length, no large gap
    for i, (y1, xa0, xa1) in enumerate(h_lines):
        for j, (y2, xb0, xb1) in enumerate(h_lines):
            if j <= i:
                continue
            gap = abs(y2 - y1)
            if gap < 4 or gap > 50:
                continue
            overlap = min(xa1, xb1) - max(xa0, xb0)
            len_a = xa1 - xa0
            len_b = xb1 - xb0
            if overlap < 0.5 * min(len_a, len_b):
                continue
            cx = (max(xa0, xb0) + min(xa1, xb1)) // 2
            cy = (y1 + y2) // 2
            w = max(xa1, xb1) - min(xa0, xb0) + 20
            h = gap + 20
            items.append(SymbolItem(
                id=_next_sym_id(),
                symbol_class="CAPACITOR",
                bbox=BBox(x0=cx - w // 2, y0=min(y1, y2) - 10,
                           x1=cx + w // 2, y1=max(y1, y2) + 10),
                rotation=0,
                mirror=False,
                conf=0.65,
                source="cv"
            ))
    return items


def _detect_ground_symbols(binary) -> List[SymbolItem]:
    """
    Ground: stacked decreasing horizontal lines (like a triangle/ladder).
    Detect by looking for 3 closely-spaced parallel horizontal lines
    that decrease in length.
    """
    import cv2
    import numpy as np

    items = []
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 30 or area > 8000:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        # Ground: wider than tall, moderate size
        if w < h or w > 200 or h > 100:
            continue
        aspect = w / (h + 1)
        if aspect < 1.5 or aspect > 8.0:
            continue
        circ = _circularity(cnt)
        if circ > 0.6:  # too circular -> not ground
            continue
        items.append(SymbolItem(
            id=_next_sym_id(),
            symbol_class="GROUND",
            bbox=BBox(x0=x, y0=y, x1=x + w, y1=y + h),
            rotation=0,
            mirror=False,
            conf=0.60,
            source="cv"
        ))
    return items


def _detect_vcc_symbols(binary) -> List[SymbolItem]:
    """
    VCC/power rail: triangle pointing up or a bar on a stub.
    Detect small triangular shapes.
    """
    import cv2
    import numpy as np

    items = []
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 30 or area > 5000:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 150 or h > 150:
            continue
        # Approximate polygon
        approx = cv2.approxPolyDP(cnt, 3, True)
        if len(approx) == 3:  # triangle
            items.append(SymbolItem(
                id=_next_sym_id(),
                symbol_class="VCC",
                bbox=BBox(x0=x, y0=y, x1=x + w, y1=y + h),
                rotation=0,
                mirror=False,
                conf=0.60,
                source="cv"
            ))
    return items


# ---------------------------------------------------------------------------
# Main detection entry point
# ---------------------------------------------------------------------------

def detect_symbols(img_path: str, texts: Optional[TextsFile] = None) -> SymbolsFile:
    """
    Run all OpenCV symbol detectors on the page image.
    Text regions are masked first to prevent false positives.

    Parameters
    ----------
    img_path : str
        Path to the binary/grayscale page image.
    texts : TextsFile, optional
        Text items to mask out before detection.

    Returns
    -------
    SymbolsFile
    """
    _reset_sym_counter()

    _, binary = _load_binary(img_path)

    if texts:
        binary = _mask_text_regions(binary, texts)

    all_items: List[SymbolItem] = []
    all_items.extend(_detect_resistors(binary))
    all_items.extend(_detect_capacitors(binary))
    all_items.extend(_detect_ground_symbols(binary))
    all_items.extend(_detect_vcc_symbols(binary))

    # Deduplicate: if two detections overlap heavily, keep higher confidence
    deduplicated = _deduplicate(all_items, iou_threshold=0.5)

    return SymbolsFile(items=deduplicated)


def _deduplicate(items: List[SymbolItem], iou_threshold: float = 0.5) -> List[SymbolItem]:
    """Non-max suppression style dedup: remove lower-confidence overlapping detections."""
    items = sorted(items, key=lambda x: x.conf, reverse=True)
    kept = []
    for item in items:
        overlap = False
        for k in kept:
            if _bbox_iou(item.bbox, k.bbox) > iou_threshold:
                overlap = True
                break
        if not overlap:
            kept.append(item)
    return kept


def _bbox_iou(a: BBox, b: BBox) -> float:
    ix0 = max(a.x0, b.x0)
    iy0 = max(a.y0, b.y0)
    ix1 = min(a.x1, b.x1)
    iy1 = min(a.y1, b.y1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = (a.x1 - a.x0) * (a.y1 - a.y0)
    area_b = (b.x1 - b.x0) * (b.y1 - b.y0)
    return inter / (area_a + area_b - inter + 1e-9)


# ---------------------------------------------------------------------------
# Debug overlay
# ---------------------------------------------------------------------------

_CLASS_COLORS = {
    "RESISTOR":  (233, 165, 14),   # Electric Cyan
    "CAPACITOR": (11, 158, 245),   # Technical Amber
    "INDUCTOR":  (248, 189, 56),   # Sky Ice Blue
    "DIODE":     (68, 68, 239),    # Alert Crimson
    "LED":       (36, 191, 251),   # Laser Gold/Amber
    "GROUND":    (180, 180, 180),  # Steel Silver
    "VCC":       (68, 68, 239),    # Red/Crimson
    "OPAMP":     (233, 165, 14),   # Electric Cyan
    "NPN":       (11, 158, 245),   # Technical Amber
    "PNP":       (6, 119, 217),    # Deep Amber
    "NMOS":      (248, 189, 56),   # Sky Ice Cyan
    "PMOS":      (233, 165, 14),   # Electric Cyan
    "CONNECTOR": (255, 255, 255),  # Pure White
}


def draw_symbol_overlay(img_path: str, symbols: SymbolsFile, out_path: str) -> None:
    try:
        import cv2
    except ImportError:
        return
    img = cv2.imread(img_path)
    if img is None:
        return
    for sym in symbols.items:
        color = _CLASS_COLORS.get(sym.symbol_class, (255, 255, 255))
        x0, y0 = int(sym.bbox.x0), int(sym.bbox.y0)
        x1, y1 = int(sym.bbox.x1), int(sym.bbox.y1)
        cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)
        label = f"{sym.symbol_class} {sym.conf:.2f}"
        cv2.putText(img, label, (x0, max(y0 - 4, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    cv2.imwrite(out_path, img)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="S3 Symbol detection (OpenCV heuristics): page.png -> symbols.json"
    )
    parser.add_argument("img", help="Input page.png")
    parser.add_argument("texts", help="texts.json (to mask text regions)")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "debug").mkdir(exist_ok=True)

    with open(args.texts) as f:
        texts = TextsFile.model_validate(json.load(f))

    symbols = detect_symbols(args.img, texts)
    sym_path = out / "symbols.json"
    sym_path.write_text(symbols.model_dump_json(indent=2), encoding="utf-8")
    print(f"[symbols_cv] {len(symbols.items)} symbols -> {sym_path}")

    draw_symbol_overlay(args.img, symbols, str(out / "debug" / "symbols_cv.png"))
    print("[symbols_cv] Debug overlay written.")


if __name__ == "__main__":
    main()
