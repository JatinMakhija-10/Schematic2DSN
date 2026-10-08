"""
vision/junctions.py  --  S5: Junction (solder dot) detection.

Rules (from config.py):
  - T-meeting: connected (always)
  - Corner-meeting: connected (always)
  - Plus (4-way) crossing: connected ONLY if a dot exists
  - Ambiguous crossings -> AMBIGUOUS_JUNCTION warning

Dots found via morphological opening with disc larger than line thickness.
Opening erases lines and leaves filled circular dots.

Outputs:
  - junctions.json  (JunctionsFile)
  - out/debug/junctions.png

CLI:
    python -m vision.junctions in/page.png in/wires.json out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import JunctionItem, JunctionsFile, Point, WiresFile
from core.config import DEFAULT_CONFIG


# ---------------------------------------------------------------------------
# Dot detection
# ---------------------------------------------------------------------------

def detect_junction_dots(img_path: str) -> List[JunctionItem]:
    """
    Find junction dots via morphological opening.
    Opening with a disc kernel removes thin lines; circular blobs that remain
    are junction dots.
    """
    import cv2
    import numpy as np

    cfg = DEFAULT_CONFIG.junction

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Cannot read: {img_path}")

    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Morphological opening with disc kernel
    r = cfg.disc_radius_px
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)
    )
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # Find connected components in the opened image
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        opened, connectivity=8
    )

    items: List[JunctionItem] = []
    for i in range(1, num_labels):  # skip background (label 0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 10:
            continue
        cx, cy = centroids[i]
        # Get contour for circularity check
        mask = (labels == i).astype(np.uint8)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        cnt = contours[0]
        perimeter = cv2.arcLength(cnt, True)
        if perimeter < 1e-3:
            continue
        circularity = 4 * 3.14159 * area / (perimeter ** 2)
        if circularity < cfg.min_circularity:
            continue

        radius = (area / 3.14159) ** 0.5
        items.append(JunctionItem(
            pos=Point(x=float(cx), y=float(cy)),
            radius=float(radius)
        ))

    return items


# ---------------------------------------------------------------------------
# Topology analysis
# ---------------------------------------------------------------------------

def classify_crossings(
    wires: WiresFile,
    dots: List[JunctionItem],
    tol: float = 6.0
) -> Tuple[List[Point], List[Point], List[dict]]:
    """
    Classify wire intersection points as:
    - connected: T-junction or corner, or 4-way crossing WITH a dot
    - ambiguous: 4-way crossing WITHOUT a dot

    Returns
    -------
    connected : List[Point]
    ambiguous : List[Point]
    warnings : List[dict]
    """
    import math

    def dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def has_dot_nearby(px: float, py: float) -> bool:
        return any(dist((px, py), (d.pos.x, d.pos.y)) < tol for d in dots)

    # Count how many segments touch each endpoint
    endpoint_count: dict = {}
    for seg in wires.segments:
        for pt in [(seg.p0.x, seg.p0.y), (seg.p1.x, seg.p1.y)]:
            endpoint_count[pt] = endpoint_count.get(pt, 0) + 1

    connected: List[Point] = []
    ambiguous: List[Point] = []
    warnings: List[dict] = []

    for pt, count in endpoint_count.items():
        p = Point(x=pt[0], y=pt[1])
        if count >= 4:
            # 4-way crossing: connected only if dot present
            cfg = DEFAULT_CONFIG.junction
            if not cfg.plus_crossing_requires_dot or has_dot_nearby(pt[0], pt[1]):
                connected.append(p)
            else:
                ambiguous.append(p)
                warnings.append({
                    "code": "AMBIGUOUS_JUNCTION",
                    "detail": f"4-way crossing at ({pt[0]:.0f},{pt[1]:.0f}) has no dot; treating as not connected.",
                    "pos": {"x": pt[0], "y": pt[1]}
                })
        elif count >= 2:
            # T or corner: always connected
            connected.append(p)

    return connected, ambiguous, warnings


def detect_junctions(img_path: str, wires: WiresFile) -> JunctionsFile:
    """
    Full S5 pipeline: detect dots + classify topology.

    Returns JunctionsFile with detected dot positions.
    Topology analysis results are used by S7 graph.
    """
    dots = detect_junction_dots(img_path)
    return JunctionsFile(items=dots)


# ---------------------------------------------------------------------------
# Debug overlay
# ---------------------------------------------------------------------------

def draw_junction_overlay(img_path: str, junctions: JunctionsFile,
                           out_path: str) -> None:
    try:
        import cv2
    except ImportError:
        return
    img = cv2.imread(img_path)
    if img is None:
        return
    for junc in junctions.items:
        cx, cy = int(junc.pos.x), int(junc.pos.y)
        r = max(4, int(junc.radius))
        cv2.circle(img, (cx, cy), r, (0, 255, 255), 2)
        cv2.circle(img, (cx, cy), 2, (0, 200, 200), -1)
    cv2.imwrite(out_path, img)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="S5 Junction detection: page.png + wires.json -> junctions.json"
    )
    parser.add_argument("img", help="Input page.png")
    parser.add_argument("wires", help="wires.json")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "debug").mkdir(exist_ok=True)

    with open(args.wires) as f:
        wires = WiresFile.model_validate(json.load(f))

    junctions = detect_junctions(args.img, wires)
    junc_path = out / "junctions.json"
    junc_path.write_text(junctions.model_dump_json(indent=2), encoding="utf-8")
    print(f"[junctions] {len(junctions.items)} dots -> {junc_path}")

    draw_junction_overlay(args.img, junctions, str(out / "debug" / "junctions.png"))
    print("[junctions] Debug overlay written.")


if __name__ == "__main__":
    main()
