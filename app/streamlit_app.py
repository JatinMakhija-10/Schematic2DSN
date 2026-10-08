"""
app/streamlit_app.py  --  Streamlit UI for Schematic2DSN.

Features:
  - Upload PDF or PNG schematic
  - Show overlay with detected components, wires, junctions
  - Show IR JSON viewer
  - Confidence breakdown (from documented formula)
  - Generate OrCAD button -> run tcl_gen + launcher
  - Rejection reason display for bad inputs

Run:
    streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from core.models import DesignIR, DesignMetadata, DesignInfo
from orcad.tcl_gen import generate_mode_a, load_ir, make_demo_ir
from orcad.launcher import launch

st.set_page_config(
    page_title="Schematic2DSN",
    page_icon="⚡",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "ir" not in st.session_state:
    st.session_state.ir = None
if "page_img" not in st.session_state:
    st.session_state.page_img = None
if "debug_images" not in st.session_state:
    st.session_state.debug_images = {}
if "tcl_script" not in st.session_state:
    st.session_state.tcl_script = None
if "reject_reason" not in st.session_state:
    st.session_state.reject_reason = None

# ---------------------------------------------------------------------------
# Helper: run the full pipeline on a file
# ---------------------------------------------------------------------------

def run_pipeline(input_path: str, out_dir: str) -> Optional[DesignIR]:
    """
    Run stages S1-S10 using the centralized core.pipeline runner.
    """
    from vision.ingest import IngestError
    from core.pipeline import run_pipeline as exec_pipeline

    try:
        ir = exec_pipeline(input_path, out_dir, generate_tcl=True)
        return ir
    except IngestError as e:
        st.session_state.reject_reason = str(e)
        return None
    except Exception as e:
        st.session_state.reject_reason = f"Pipeline error: {e}"
        return None


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.title("⚡ Schematic2DSN")
st.caption("Upload a schematic PDF or PNG → get an editable OrCAD Capture design.")

col_upload, col_demo = st.columns([3, 1])
with col_upload:
    uploaded = st.file_uploader(
        "Upload schematic (PDF, PNG, JPG)",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
with col_demo:
    if st.button("Load Demo IR (R+C+GND+VCC)"):
        st.session_state.ir = make_demo_ir()
        st.session_state.reject_reason = None

# Run pipeline on upload
if uploaded is not None:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, uploaded.name)
        with open(input_path, "wb") as f:
            f.write(uploaded.read())

        out_dir = os.path.join(tmpdir, "out")
        os.makedirs(os.path.join(out_dir, "debug"), exist_ok=True)

        with st.spinner("Analyzing schematic..."):
            ir = run_pipeline(input_path, out_dir)

        if ir is not None:
            st.session_state.ir = ir
            st.session_state.reject_reason = None

            # Cache debug images
            debug_dir = os.path.join(out_dir, "debug")
            for name in ["text.png", "wires.png", "symbols.png", "junctions.png"]:
                p = os.path.join(debug_dir, name)
                if os.path.exists(p):
                    with open(p, "rb") as f:
                        st.session_state.debug_images[name] = f.read()

            page_p = os.path.join(out_dir, "page.png")
            if os.path.exists(page_p):
                with open(page_p, "rb") as f:
                    st.session_state.page_img = f.read()

# Show rejection reason
if st.session_state.reject_reason:
    st.error(f"❌ **Rejected**: {st.session_state.reject_reason}")
    st.stop()

# Show results if IR is available
ir: Optional[DesignIR] = st.session_state.ir

if ir is None:
    st.info("Upload a schematic PDF or PNG to begin, or load the demo IR.")
    st.stop()

# --- Summary ---
confidence = ir.metadata.confidence if ir.metadata else 0.0
n_comp = len(ir.components)
n_nets = len(ir.nets)
n_warn = len(ir.warnings)

st.success(
    f"✅ **{n_comp} components**, **{n_nets} nets** | "
    f"Confidence: **{confidence:.0%}** | Warnings: {n_warn}"
)

tab_overlay, tab_ir, tab_report, tab_tcl = st.tabs(
    ["🖼 Overlay", "📄 IR JSON", "📊 Report", "🔧 Generate OrCAD"]
)

with tab_overlay:
    if st.session_state.page_img:
        overlay_choice = st.selectbox(
            "Debug layer", ["Original", "Text", "Wires", "Symbols", "Junctions"]
        )
        name_map = {
            "Text": "text.png",
            "Wires": "wires.png",
            "Symbols": "symbols.png",
            "Junctions": "junctions.png",
        }
        if overlay_choice == "Original":
            st.image(st.session_state.page_img, use_column_width=True)
        else:
            key = name_map.get(overlay_choice)
            img_data = st.session_state.debug_images.get(key)
            if img_data:
                st.image(img_data, use_column_width=True)
            else:
                st.warning("Overlay not available (run full pipeline on an uploaded file).")
    else:
        st.info("Overlay available after uploading a file (demo mode shows JSON only).")

with tab_ir:
    st.json(ir.model_dump())

with tab_report:
    # Confidence breakdown
    st.subheader("Confidence Formula")
    st.code(
        "confidence = 0.35 * mean(symbol_conf)\n"
        "           + 0.25 * ocr_confidence\n"
        "           + 0.25 * fraction_pins_connected\n"
        "           + 0.15 * fraction_nets_with_2plus_pins\n"
        "           - 0.05 * min(n_warnings, 10) / 10",
        language="text"
    )

    st.subheader("Warnings")
    if not ir.warnings:
        st.success("No warnings.")
    else:
        for w in ir.warnings:
            st.warning(f"**{w.code}** – {w.detail}")

    st.subheader("Components")
    comp_data = [
        {
            "ID": c.id,
            "Class": c.symbol_class,
            "Value": c.value,
            "Confidence": f"{c.confidence:.0%}",
            "Pins": len(c.pins),
        }
        for c in ir.components
    ]
    st.dataframe(comp_data, use_container_width=True)

    st.subheader("Nets")
    net_data = [
        {
            "Name": n.name,
            "Auto-named": n.auto_named,
            "Pins": len(n.pins),
            "Labels": ", ".join(l.text for l in n.labels),
        }
        for n in ir.nets
    ]
    st.dataframe(net_data, use_container_width=True)

with tab_tcl:
    st.subheader("Generate OrCAD Design (Mode A)")
    lib_path = st.text_input(
        "Library path (.olb)",
        value="orcad/library/COMPETITION.olb"
    )

    if st.button("Generate Tcl Script"):
        with st.spinner("Generating..."):
            try:
                tcl = generate_mode_a(ir, lib_path=lib_path)
                st.session_state.tcl_script = tcl
            except Exception as e:
                st.error(f"Generation failed: {e}")

    if st.session_state.tcl_script:
        tcl = st.session_state.tcl_script
        st.code(tcl, language="tcl")
        st.download_button(
            "Download design.tcl",
            data=tcl.encode(),
            file_name="design.tcl",
            mime="text/plain"
        )

        st.subheader("Launch Capture")
        st.info(
            "Launcher is in **manual** mode. Download the Tcl above, open OrCAD Capture, "
            "create a project, and run in the command window:\n\n"
            "`source C:/path/to/design.tcl`\n\n"
            "After Day 0 journaling, update `LAUNCH_MODE` in `orcad/launcher.py`."
        )
