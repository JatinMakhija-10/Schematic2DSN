"""
vision/ingest.py  --  Stage S1: Ingest PDF or PNG input.

Outputs:
  - page.png   (rendered page image at target DPI)
  - page.meta.json  (PageMeta pydantic model)

CLI:
    python -m vision.ingest input.pdf out/
    python -m vision.ingest input.png out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import PageMeta
from core.config import DEFAULT_CONFIG


class IngestError(RuntimeError):
    """Raised when the input cannot be ingested. Message includes a machine code."""
    pass


REJECT_CODES = {
    "MULTI_PAGE":       "Input PDF has multiple pages. Only single-page inputs are supported.",
    "LOW_DPI":          "DPI equivalent is below minimum threshold.",
    "IMAGE_TOO_SMALL":  "Image is below minimum size on the long side.",
    "OFF_AXIS_WIRES":   "Too many off-axis line segments; diagonal wires not supported.",
    "COLOR_PHOTO":      "Input appears to be a color photo, not a schematic.",
    "UNSUPPORTED_TYPE": "Input file type not supported. Use PDF or PNG/JPG.",
}


def ingest(input_path: str, out_dir: str) -> PageMeta:
    """
    Ingest a PDF or PNG and produce page.png + page.meta.json.

    Parameters
    ----------
    input_path : str
        Path to the input file.
    out_dir : str
        Directory to write outputs.

    Returns
    -------
    PageMeta
        Metadata about the ingested page.

    Raises
    ------
    IngestError
        With a machine-readable code if the input is rejected.
    """
    cfg = DEFAULT_CONFIG.ingest
    path = Path(input_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    debug_dir = out / 'debug'
    debug_dir.mkdir(exist_ok=True)

    if not path.is_file():
        raise IngestError(f"FILE_NOT_FOUND: Input file does not exist: {path}")

    suffix = path.suffix.lower()

    if suffix == '.pdf':
        meta = _ingest_pdf(path, out, cfg)
    elif suffix in ('.png', '.jpg', '.jpeg', '.tif', '.tiff'):
        meta = _ingest_raster(path, out, cfg)
    else:
        raise IngestError(f"UNSUPPORTED_TYPE: {REJECT_CODES['UNSUPPORTED_TYPE']}")

    # Write metadata
    meta_path = out / 'page.meta.json'
    meta_path.write_text(meta.model_dump_json(indent=2), encoding='utf-8')
    print(f"[ingest] mode={meta.mode} size={meta.width_px}x{meta.height_px} dpi={meta.dpi:.0f}")
    print(f"[ingest] Wrote: {out / 'page.png'}, {meta_path}")
    return meta


def _ingest_pdf(path: Path, out: Path, cfg) -> PageMeta:
    try:
        import pymupdf as fitz
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install PyMuPDF")

    doc = fitz.open(str(path))
    if doc.page_count > 1:
        raise IngestError(f"MULTI_PAGE: {REJECT_CODES['MULTI_PAGE']}")

    page = doc[0]

    # Detect vector vs raster
    drawings = page.get_drawings()
    total_drawing_items = sum(len(d.get("items", [])) for d in drawings)
    is_vector = (len(drawings) >= cfg.min_vector_paths) or (total_drawing_items >= cfg.min_vector_paths)

    dpi = cfg.render_dpi
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)

    if pix.width < cfg.min_image_long_side_px and pix.height < cfg.min_image_long_side_px:
        raise IngestError(f"IMAGE_TOO_SMALL: {REJECT_CODES['IMAGE_TOO_SMALL']}")

    img_path = out / 'page.png'
    pix.save(str(img_path))

    # Compute pixel_per_mil_hint from PDF page size (1 point = 1/72 inch = 1000/72 mils)
    page_width_pts = page.rect.width
    page_height_pts = page.rect.height
    page_width_mils = page_width_pts * (1000 / 72)
    pixel_per_mil_hint = pix.width / page_width_mils

    return PageMeta(
        source=str(path),
        mode='vector' if is_vector else 'raster',
        width_px=pix.width,
        height_px=pix.height,
        dpi=float(dpi),
        pixel_per_mil_hint=pixel_per_mil_hint,
        page_index=0,
    )


def _ingest_raster(path: Path, out: Path, cfg) -> PageMeta:
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise ImportError("OpenCV not installed. Run: pip install opencv-python")

    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise IngestError(f"UNSUPPORTED_TYPE: Cannot read image file {path}")

    h, w = img.shape
    long_side = max(w, h)
    if long_side < cfg.min_image_long_side_px:
        raise IngestError(f"IMAGE_TOO_SMALL: {REJECT_CODES['IMAGE_TOO_SMALL']}")

    # Assume 600 DPI if not embedded in file
    dpi = 600.0

    img_path = out / 'page.png'
    cv2.imwrite(str(img_path), img)

    return PageMeta(
        source=str(path),
        mode='raster',
        width_px=w,
        height_px=h,
        dpi=dpi,
        pixel_per_mil_hint=None,
        page_index=0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="S1 Ingest: PDF or PNG -> page.png + page.meta.json"
    )
    parser.add_argument("input", help="Input PDF or image file")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    try:
        ingest(args.input, args.out_dir)
    except IngestError as e:
        print(f"REJECT: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
