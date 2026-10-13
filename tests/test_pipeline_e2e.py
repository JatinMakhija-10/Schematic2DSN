"""
tests/test_pipeline_e2e.py  --  End-to-end integration tests for full pipeline execution.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import DesignIR
from core.pipeline import run_pipeline
from data.synthetic.render_synthetic import render_ir_to_png
from data.synthetic.generate_test_circuits import voltage_divider, rc_filter


def test_pipeline_e2e_raster_mode_a(tmp_path):
    ir_gt = voltage_divider()
    img_path = tmp_path / "voltage_divider.png"
    render_ir_to_png(ir_gt, str(img_path))

    out_dir = tmp_path / "out_mode_a"
    ir = run_pipeline(
        input_path=str(img_path),
        out_dir=str(out_dir),
        generate_tcl=True,
        export_mode="A"
    )

    assert isinstance(ir, DesignIR)
    assert (out_dir / "page.png").exists()
    assert (out_dir / "page.meta.json").exists()
    assert (out_dir / "texts.json").exists()
    assert (out_dir / "symbols.json").exists()
    assert (out_dir / "wires.json").exists()
    assert (out_dir / "junctions.json").exists()
    assert (out_dir / "design.json").exists()
    assert (out_dir / "design.tcl").exists()

    tcl = (out_dir / "design.tcl").read_text(encoding="utf-8")
    assert "PlacePart" in tcl
    assert "SaveDesign" in tcl


def test_pipeline_e2e_raster_mode_b(tmp_path):
    ir_gt = rc_filter()
    img_path = tmp_path / "rc_filter.png"
    render_ir_to_png(ir_gt, str(img_path))

    out_dir = tmp_path / "out_mode_b"
    ir = run_pipeline(
        input_path=str(img_path),
        out_dir=str(out_dir),
        generate_tcl=True,
        export_mode="B"
    )

    assert isinstance(ir, DesignIR)
    assert (out_dir / "design.tcl").exists()

    tcl = (out_dir / "design.tcl").read_text(encoding="utf-8")
    assert "PlacePart" in tcl
    assert "Mode B Routed" in tcl
    assert "SaveDesign" in tcl
