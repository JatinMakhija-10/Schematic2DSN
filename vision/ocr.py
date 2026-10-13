"""
vision/ocr.py  --  S2 raster path: PaddleOCR text extraction.

Runs PaddleOCR at 0 and 90 degrees on the page image, merges results,
applies regex post-processing for refdes and value strings.

Outputs:
  - texts.json  (TextsFile)
  - out/debug/ocr.png

CLI:
    python -m vision.ocr in/page.png out/
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import TextItem, TextsFile, BBox, Point
from core.config import DEFAULT_CONFIG
from core.units import normalize_value, fix_refdes, REFDES_PATTERN


def _iou(a: BBox, b: BBox) -> float:
    """Intersection over union for two bounding boxes."""
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


def _merge_by_confidence(items_0deg: List[TextItem],
                          items_90deg: List[TextItem],
                          iou_threshold: float = 0.3) -> List[TextItem]:
    """
    Merge OCR results from two rotations.
    For overlapping boxes (IoU > threshold), keep the one with higher confidence.
    """
    merged = list(items_0deg)
    for item in items_90deg:
        matched = False
        for existing in merged:
            if _iou(existing.bbox, item.bbox) > iou_threshold:
                if item.conf > existing.conf:
                    merged.remove(existing)
                    merged.append(item)
                matched = True
                break
        if not matched:
            merged.append(item)
    return merged


def _postprocess(items: List[TextItem]) -> List[TextItem]:
    """
    Apply regex-based OCR corrections for refdes and value strings.
    Does NOT blindly replace characters - only when pattern matches.
    """
    result = []
    for item in items:
        text = item.text.strip()
        # Try refdes fix
        fixed = fix_refdes(text)
        # Try value normalization
        try:
            norm = normalize_value(text)
        except Exception:
            norm = text
        # Use fixed refdes if it differs and is valid
        if REFDES_PATTERN.match(fixed) and fixed != text:
            text = fixed
        elif norm != text:
            text = norm
        result.append(item.model_copy(update={"text": text}))
    return result


def run_ocr(img_path: str) -> TextsFile:
    """
    Run OCR on an image and return extracted text items.
    Runs at 0 deg and 90 deg, merges by confidence.
    Supports PaddleOCR and RapidOCR (ONNX runtime), with graceful fallback.
    """
    engine_name = None
    paddle_ocr = None
    rapid_ocr = None

    try:
        from paddleocr import PaddleOCR
        paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        engine_name = "paddle"
    except Exception:
        try:
            from rapidocr_onnxruntime import RapidOCR
            rapid_ocr = RapidOCR()
            engine_name = "rapid"
        except Exception:
            print("[ocr] WARNING: Neither PaddleOCR nor RapidOCR available. Returning empty texts.")
            return TextsFile(items=[])

    try:
        import cv2
        import numpy as np
    except ImportError:
        print("[ocr] WARNING: OpenCV not installed.")
        return TextsFile(items=[])

    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {img_path}")

    h, w = img.shape[:2]

    # OCR at 0 degrees
    if engine_name == "paddle":
        results_0 = paddle_ocr.ocr(img_path, cls=True)
    else:
        rapid_res, _ = rapid_ocr(img)
        # Format rapidocr output to match paddleocr structure: [[box, (text, conf)]]
        results_0 = [[(item[0], (item[1], float(item[2]))) for item in rapid_res]] if rapid_res else [[]]

    # OCR at 90 degrees (for vertical text on rotated components)
    img_90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp_90 = tf.name
    try:
        cv2.imwrite(tmp_90, img_90)
        if engine_name == "paddle":
            results_90_raw = paddle_ocr.ocr(tmp_90, cls=True)
        else:
            rapid_res_90, _ = rapid_ocr(tmp_90)
            results_90_raw = [[(item[0], (item[1], float(item[2]))) for item in rapid_res_90]] if rapid_res_90 else [[]]
    finally:
        if os.path.exists(tmp_90):
            try:
                os.unlink(tmp_90)
            except OSError:
                pass

    def parse_results(results, rotation_deg: float = 0.0,
                      img_w: int = 0, img_h: int = 0) -> List[TextItem]:
        items = []
        if not results or results[0] is None:
            return items
        for line in results[0]:
            box, (text, conf) = line
            # box is [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            if rotation_deg == 90:
                # Transform back from 90-deg rotated image coords
                # In rotated img: (rx, ry) -> original: (ry, img_w - rx)
                x0_orig = y0
                y0_orig = img_w - x1
                x1_orig = y1
                y1_orig = img_w - x0
                x0, y0, x1, y1 = x0_orig, y0_orig, x1_orig, y1_orig
            items.append(TextItem(
                text=text.strip(),
                bbox=BBox(x0=x0, y0=y0, x1=x1, y1=y1),
                angle=rotation_deg,
                conf=float(conf),
                source="ocr"
            ))
        return items

    items_0 = parse_results(results_0, 0.0)
    items_90 = parse_results(results_90_raw, 90.0, img_w=w, img_h=h)

    merged = _merge_by_confidence(items_0, items_90)
    processed = _postprocess(merged)

    return TextsFile(items=processed)


def draw_ocr_overlay(img_path: str, texts: TextsFile, out_path: str) -> None:
    try:
        import cv2
    except ImportError:
        return
    img = cv2.imread(img_path)
    if img is None:
        return
    for item in texts.items:
        x0, y0 = int(item.bbox.x0), int(item.bbox.y0)
        x1, y1 = int(item.bbox.x1), int(item.bbox.y1)
        color = (233, 165, 14) if item.conf > 0.8 else (11, 158, 245)
        cv2.rectangle(img, (x0, y0), (x1, y1), color, 1)
        label = f"{item.text[:15]} ({item.conf:.2f})"
        cv2.putText(img, label, (x0, max(y0 - 2, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
    cv2.imwrite(out_path, img)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="S2 OCR: page.png -> texts.json"
    )
    parser.add_argument("img", help="Input page.png")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "debug").mkdir(exist_ok=True)

    texts = run_ocr(args.img)
    texts_path = out / "texts.json"
    texts_path.write_text(texts.model_dump_json(indent=2), encoding="utf-8")
    print(f"[ocr] {len(texts.items)} text items -> {texts_path}")

    draw_ocr_overlay(args.img, texts, str(out / "debug" / "ocr.png"))
    print("[ocr] Debug overlay written.")


if __name__ == "__main__":
    main()
