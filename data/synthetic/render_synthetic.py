"""
data/synthetic/render_synthetic.py  --  Render synthetic schematic diagrams to PDF and PNG.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN

Generates real vector PDF and raster PNG files from ground-truth DesignIR structures.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.models import DesignIR, Point
from core.geometry import CoordTransform


def _get_scale_params(ir: DesignIR, target_w: float, target_h: float, margin: float):
    all_x = [c.position.x for c in ir.components] + [p.pos.x for c in ir.components for p in c.pins]
    all_y = [c.position.y for c in ir.components] + [p.pos.y for c in ir.components for p in c.pins]
    if not all_x or not all_y:
        return 3000, 2000, 0.45, 50, 50
    min_x, max_x = min(all_x) - 150, max(all_x) + 150
    min_y, max_y = min(all_y) - 150, max(all_y) + 150
    span_x = max(max_x - min_x, 800)
    span_y = max(max_y - min_y, 800)
    avail_w = target_w - 2 * margin
    avail_h = target_h - 2 * margin
    scale = min(avail_w / span_x, avail_h / span_y)
    offset_x = margin + (avail_w - span_x * scale) / 2
    offset_y = margin + (avail_h - span_y * scale) / 2
    return min_x, min_y, scale, offset_x, offset_y


def render_ir_to_pdf(ir: DesignIR, output_pdf_path: str) -> None:
    """
    Render DesignIR as a vector PDF using PyMuPDF.
    Draws wires, components as labeled blocks/symbols, and text annotations.
    """
    import pymupdf as fitz

    doc = fitz.open()
    # Sheet: 1100 x 850 points
    page_w, page_h = 1100, 850
    page = doc.new_page(width=page_w, height=page_h)

    min_x, min_y, scale, off_x, off_y = _get_scale_params(ir, page_w, page_h, margin=60)

    def mils_to_pts(mx: float, my: float) -> fitz.Point:
        x_pt = (mx - min_x) * scale + off_x
        y_pt = page_h - ((my - min_y) * scale + off_y)
        return fitz.Point(x_pt, y_pt)

    shape = page.new_shape()

    # Draw components
    for comp in ir.components:
        cp = mils_to_pts(comp.position.x, comp.position.y)
        hw = 35 if len(comp.pins) <= 2 else 50
        hh = 18 if len(comp.pins) <= 2 else max(25, (len(comp.pins) // 2) * 12)
        r = fitz.Rect(cp.x - hw, cp.y - hh, cp.x + hw, cp.y + hh)
        shape.draw_rect(r)

        # Label
        text_label = f"{comp.id}"
        if comp.value:
            text_label += f" {comp.value}"
        page.insert_text(fitz.Point(cp.x - hw + 5, cp.y + 4), text_label, fontsize=8)

        # Pins stubs
        for pin in comp.pins:
            pp = mils_to_pts(pin.pos.x, pin.pos.y)
            shape.draw_line(cp, pp)

    # Draw net connections between pins
    for net in ir.nets:
        if len(net.pins) >= 2:
            pts = []
            for pref in net.pins:
                cid, pnum = pref[0], pref[1]
                for c in ir.components:
                    if c.id == cid:
                        for p in c.pins:
                            if p.number == pnum:
                                pts.append(mils_to_pts(p.pos.x, p.pos.y))
            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    p0 = pts[i]
                    p1 = pts[i + 1]
                    corner = fitz.Point(p1.x, p0.y)
                    shape.draw_line(p0, corner)
                    shape.draw_line(corner, p1)

    shape.finish(color=(0, 0, 0), width=1.5)
    shape.commit()

    Path(output_pdf_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf_path)
    doc.close()


def render_ir_to_png(ir: DesignIR, output_png_path: str, dpi: int = 300) -> None:
    """
    Render DesignIR to a clean raster PNG schematic.
    """
    import cv2
    import numpy as np

    # 1600 x 1300 image (high resolution for S1 Ingest check)
    w, h = 1600, 1300
    img = np.ones((h, w, 3), dtype=np.uint8) * 255

    min_x, min_y, scale, off_x, off_y = _get_scale_params(ir, w, h, margin=100)

    def mils_to_px(mx: float, my: float):
        px = int((mx - min_x) * scale + off_x)
        py = int(h - ((my - min_y) * scale + off_y))
        return px, py

    # Draw components
    for comp in ir.components:
        cx, cy = mils_to_px(comp.position.x, comp.position.y)
        hw = 45 if len(comp.pins) <= 2 else 70
        hh = 24 if len(comp.pins) <= 2 else max(35, (len(comp.pins) // 2) * 16)
        cv2.rectangle(img, (cx - hw, cy - hh), (cx + hw, cy + hh), (0, 0, 0), 2)
        label = f"{comp.id} {comp.value}".strip()
        cv2.putText(img, label, (cx - hw + 8, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

        for pin in comp.pins:
            px, py = mils_to_px(pin.pos.x, pin.pos.y)
            cv2.line(img, (cx, cy), (px, py), (0, 0, 0), 2)

    # Draw wires
    for net in ir.nets:
        pts = []
        for pref in net.pins:
            cid, pnum = pref[0], pref[1]
            for c in ir.components:
                if c.id == cid:
                    for p in c.pins:
                        if p.number == pnum:
                            pts.append(mils_to_px(p.pos.x, p.pos.y))
        if len(pts) >= 2:
            for i in range(len(pts) - 1):
                p0 = pts[i]
                p1 = pts[i + 1]
                corner = (p1[0], p0[1])
                cv2.line(img, p0, corner, (0, 0, 0), 2)
                cv2.line(img, corner, p1, (0, 0, 0), 2)

    Path(output_png_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_png_path, img)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render synthetic schematics to PDF/PNG")
    parser.add_argument("design_json", help="Path to design.json")
    parser.add_argument("out_prefix", help="Output prefix (e.g. out/test)")
    args = parser.parse_args()

    with open(args.design_json, encoding="utf-8") as f:
        ir = DesignIR.model_validate(json.load(f))

    pdf_out = f"{args.out_prefix}.pdf"
    png_out = f"{args.out_prefix}.png"
    render_ir_to_pdf(ir, pdf_out)
    render_ir_to_png(ir, png_out)
    print(f"[render] Generated {pdf_out} and {png_out}")


if __name__ == "__main__":
    main()
