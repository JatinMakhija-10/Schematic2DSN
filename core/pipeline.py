"""
core/pipeline.py  --  End-to-end Schematic2DSN reconstruction pipeline.

Runs Stages S1 through S10:
  S1 Ingest (PDF / raster image -> page.png, page.meta.json)
  S2 Text (Vector dict or OCR -> texts.json)
  S3 Symbols (OpenCV heuristics / YOLO / fallback -> symbols.json)
  S4 Wires (Vector line segments or raster skeleton+Hough -> wires.json)
  S5 Junctions (Solder dots & topology classification -> junctions.json)
  S6 Pins (Expected pin positions from library contract, snapped to wires)
  S7 Graph (Union-find net extraction & label association)
  S8 Associate (Hungarian matching of RefDes and Values)
  S9 Validate (Design rules, warnings, confidence score -> design.json)
  S10 Export (Generate OrCAD Mode A / Mode B Tcl -> design.tcl)

CLI:
    python -m core.pipeline input.pdf out/
    python -m core.pipeline input.png out/ --generate-tcl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import (
    DesignIR, DesignInfo, DesignMetadata,
    ComponentIR, PinIR, NetIR, WarningIR, Point, BBox,
    PageMeta, TextsFile, SymbolsFile, WiresFile, JunctionsFile
)
from core.config import DEFAULT_CONFIG
from core.geometry import CoordTransform, estimate_scale_from_passives
from vision.ingest import ingest, IngestError
from orcad.tcl_gen import generate_mode_a


def run_pipeline(
    input_path: str,
    out_dir: str,
    lib_path: str = "orcad/library/COMPETITION.olb",
    generate_tcl: bool = True
) -> DesignIR:
    """
    Execute full pipeline end-to-end on a schematic file.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    debug_dir = out_path / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # S1: Ingest
    # -----------------------------------------------------------------------
    meta = ingest(input_path, str(out_path))
    page_img_path = str(out_path / "page.png")

    # -----------------------------------------------------------------------
    # S2 & S4: Text and Wires
    # -----------------------------------------------------------------------
    if meta.mode == "vector":
        from vision.vector_extract import (
            extract_vector_text, extract_vector_wires,
            draw_text_overlay, draw_wire_overlay
        )
        texts = extract_vector_text(input_path)
        (out_path / "texts.json").write_text(texts.model_dump_json(indent=2), encoding="utf-8")
        draw_text_overlay(page_img_path, texts, str(debug_dir / "text.png"))

        wires = extract_vector_wires(input_path)
        (out_path / "wires.json").write_text(wires.model_dump_json(indent=2), encoding="utf-8")
        draw_wire_overlay(page_img_path, wires, str(debug_dir / "wires.png"))
    else:
        from vision.ocr import run_ocr, draw_ocr_overlay
        from vision.wires import detect_wires, draw_wire_overlay
        texts = run_ocr(page_img_path)
        (out_path / "texts.json").write_text(texts.model_dump_json(indent=2), encoding="utf-8")
        draw_ocr_overlay(page_img_path, texts, str(debug_dir / "text.png"))

        wires = detect_wires(page_img_path, None, texts)
        (out_path / "wires.json").write_text(wires.model_dump_json(indent=2), encoding="utf-8")
        draw_wire_overlay(page_img_path, wires, str(debug_dir / "wires.png"))

    # -----------------------------------------------------------------------
    # S3: Symbols
    # -----------------------------------------------------------------------
    from vision.symbols_cv import detect_symbols, draw_symbol_overlay
    symbols = detect_symbols(page_img_path, texts)
    (out_path / "symbols.json").write_text(symbols.model_dump_json(indent=2), encoding="utf-8")
    draw_symbol_overlay(page_img_path, symbols, str(debug_dir / "symbols.png"))

    # -----------------------------------------------------------------------
    # S5: Junctions
    # -----------------------------------------------------------------------
    from vision.junctions import detect_junctions, draw_junction_overlay
    junctions = detect_junctions(page_img_path, wires)
    (out_path / "junctions.json").write_text(junctions.model_dump_json(indent=2), encoding="utf-8")
    draw_junction_overlay(page_img_path, junctions, str(debug_dir / "junctions.png"))

    # -----------------------------------------------------------------------
    # S8: Associate RefDes and Values to Symbols
    # -----------------------------------------------------------------------
    from circuit.associate import associate
    components, assoc_warnings = associate(symbols, texts)

    # -----------------------------------------------------------------------
    # Scale Estimation & S6: Pins
    # -----------------------------------------------------------------------
    passives = [s for s in symbols.items if s.symbol_class in ("RESISTOR", "CAPACITOR", "INDUCTOR", "DIODE")]
    body_lengths = [max(p.bbox.width, p.bbox.height) for p in passives if max(p.bbox.width, p.bbox.height) > 10]

    if meta.pixel_per_mil_hint:
        scale_px_per_mil = meta.pixel_per_mil_hint
    elif body_lengths:
        scale_px_per_mil = estimate_scale_from_passives(body_lengths, nominal_body_mils=200.0)
    else:
        # Default fallback: 600 DPI -> 0.6 px/mil
        scale_px_per_mil = 0.6

    from core.config import DEFAULT_CONFIG
    sheet_h_mils = DEFAULT_CONFIG.orcad.sheet_sizes_mils.get("A", (11000, 8500))[1]
    xfm = CoordTransform(
        scale_px_per_mil=scale_px_per_mil,
        sheet_height_mils=sheet_h_mils,
        origin_px=(0.0, 0.0)
    )

    from vision.pins import compute_pin_positions, snap_pins_to_wires
    pin_map: Dict[str, List[Tuple[str, str, Point]]] = {}
    snap_tol_px = DEFAULT_CONFIG.pin.snap_tolerance_px

    # Map each component back to its symbol and compute/snap pins
    sym_by_id = {s.id: s for s in symbols.items}
    # Track component by symbol source or position
    for comp in components:
        matched_sym = None
        for s in symbols.items:
            if s.symbol_class == comp.symbol_class and abs(s.bbox.cx - comp.position.x) < 5 and abs(s.bbox.cy - comp.position.y) < 5:
                matched_sym = s
                break
        if matched_sym:
            raw_pins = compute_pin_positions(matched_sym, scale_px_per_mil)
            snapped = snap_pins_to_wires(raw_pins, wires, snap_tol_px)
            # Transform positions to mils for ComponentIR
            mils_pins: List[PinIR] = []
            for sp in snapped:
                mp = xfm.px_point_to_mils(sp.pos)
                smx, smy = xfm.snap_to_grid(mp.x, mp.y, grid=DEFAULT_CONFIG.orcad.grid_mils)
                mils_pins.append(PinIR(
                    number=sp.number,
                    function=sp.function,
                    pos=Point(x=float(smx), y=float(smy)),
                    net=None
                ))
            comp.pins = mils_pins
            # Store in pin_map in pixel coordinates for graph net discovery
            pin_map[comp.id] = [(sp.number, sp.function, sp.pos) for sp in snapped]

        # Convert component position from pixels to mils
        m_pos = xfm.px_point_to_mils(comp.position)
        smx, smy = xfm.snap_to_grid(m_pos.x, m_pos.y, grid=DEFAULT_CONFIG.orcad.grid_mils)
        comp.position = Point(x=float(smx), y=float(smy))

    # -----------------------------------------------------------------------
    # S7: Graph
    # -----------------------------------------------------------------------
    from circuit.graph import build_graph
    nets, graph_warnings = build_graph(
        wires=wires,
        junctions=junctions,
        symbols=symbols,
        texts=texts,
        pin_map=pin_map,
        scale_px_per_mil=scale_px_per_mil
    )

    # Attach net names back to component pins
    for net in nets:
        for p_ref in net.pins:
            c_id, p_num = p_ref[0], p_ref[1]
            for comp in components:
                if comp.id == c_id:
                    for p in comp.pins:
                        if p.number == p_num:
                            p.net = net.name

    # -----------------------------------------------------------------------
    # S9: Validate & IR assembly
    # -----------------------------------------------------------------------
    ir = DesignIR(
        design=DesignInfo(name=Path(input_path).stem),
        components=components,
        nets=nets,
        warnings=assoc_warnings + graph_warnings,
        metadata=DesignMetadata(
            source=str(input_path),
            mode=meta.mode,
            confidence=0.0,
            ocr_confidence=1.0 if meta.mode == "vector" else 0.8
        )
    )

    from circuit.validate import validate
    ir, confidence = validate(ir)

    design_json_path = out_path / "design.json"
    design_json_path.write_text(ir.model_dump_json(indent=2), encoding="utf-8")

    # -----------------------------------------------------------------------
    # S10: Export OrCAD Tcl
    # -----------------------------------------------------------------------
    if generate_tcl:
        tcl_path = out_path / "design.tcl"
        generate_mode_a(ir, lib_path=lib_path, output_path=str(tcl_path))

    return ir


def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end Schematic2DSN pipeline")
    parser.add_argument("input", help="Input schematic PDF or image")
    parser.add_argument("out_dir", help="Output directory")
    parser.add_argument("--lib", default="orcad/library/COMPETITION.olb", help="OrCAD OLB library path")
    parser.add_argument("--no-tcl", action="store_true", help="Do not generate Tcl script")
    args = parser.parse_args()

    ir = run_pipeline(
        input_path=args.input,
        out_dir=args.out_dir,
        lib_path=args.lib,
        generate_tcl=not args.no_tcl
    )
    conf = ir.metadata.confidence if ir.metadata else 0.0
    print(f"[pipeline] Successfully processed {args.input}")
    print(f"[pipeline] Components: {len(ir.components)}, Nets: {len(ir.nets)}, Confidence: {conf:.1%}")
    print(f"[pipeline] Output saved to {args.out_dir}")


if __name__ == "__main__":
    main()
