# ⚡ Schematic2DSN

[![CI](https://github.com/JatinMakhija-10/Schematic2DSN/actions/workflows/ci.yml/badge.svg)](https://github.com/JatinMakhija-10/Schematic2DSN/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Author-%40JatinMakhija--10-0ea5e9.svg)](https://github.com/JatinMakhija-10)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Schematic2DSN-181717?logo=github)](https://github.com/JatinMakhija-10/Schematic2DSN)
[![Tests Passing](https://img.shields.io/badge/tests-151%20passed-0ea5e9.svg)](https://github.com/JatinMakhija-10/Schematic2DSN)

> **We do not draw a picture of the schematic; we reconstruct the circuit graph and compile it into a native, fully editable Cadence OrCAD Capture design.**

Developed by **[Jatin Makhija](https://github.com/JatinMakhija-10)** ([@JatinMakhija-10](https://github.com/JatinMakhija-10))  
Repository: [https://github.com/JatinMakhija-10/Schematic2DSN](https://github.com/JatinMakhija-10/Schematic2DSN)

---

## 🎯 Vision & Core Philosophy

**Schematic2DSN** takes a schematic diagram (vector PDF or raster image PNG/JPG) and automatically extracts its electrical topology, components, reference designators, values, and nets into an Intermediate Representation (`design.json`). It then compiles this IR into journal-verified Cadence OrCAD Capture Tcl automation scripts to produce an editable `.DSN` schematic where parts and wires can be moved, edited, and simulated.

```
Input Schematic (PDF / PNG)
           │
  [S1 Ingest]         ──► page.png, page.meta.json (Vector / Raster detection)
           │
  [S2 Text Extraction] ──► texts.json (PyMuPDF spans or RapidOCR / PaddleOCR)
  [S3 Symbol Detector] ──► symbols.json (13 classes: R, C, L, D, LED, Q, U, M, J, GND, VCC)
  [S4 Wire Extraction] ──► wires.json (Orthogonal skeleton segments & endpoints)
  [S5 Solder Dots]     ──► junctions.json (Morphological circular dot detection)
           │
  [S6 Pin Snapping]    ──► Library contract offsets snapped to wire endpoints
  [S7 Graph Engine]    ──► Union-Find net extraction & global label propagation
  [S8 Hungarian Match] ──► Optimal bipartite RefDes & value assignment
  [S9 ERC Validator]   ──► design.json (IR) + confidence scoring + ERC warnings
           │
  [S10 OrCAD Exporter] ──► design.tcl (Mode A stubs or Mode B routed polylines)
  [S11 Round-Trip]     ──► Canonical netlist verification & automated proof
```

---

## 🏆 Key Features

- **Dual Extraction Pathways**:
  - **Vector Path**: Directly extracts vector line drawings and text spans via PyMuPDF (`get_drawings()` and `get_text("dict")`), achieving mathematically exact coordinate preservation.
  - **Raster Path**: Robust pipeline with Otsu thresholding, morphological skeleton thinning, probabilistic Hough transforms, and collinear segment merging.
- **Robust OCR**: Dual 0°/90° angle sweeps with confidence merging via RapidOCR (ONNX) and PaddleOCR, plus domain regex normalization (`4k7` ➔ `4.7k`, `100R` ➔ `100ohm`, `RI` ➔ `R1`).
- **Optimal Association**: Uses the Hungarian algorithm (`scipy.optimize.linear_sum_assignment`) to match components with RefDes and value strings while avoiding duplicated assignments.
- **13 Component Classes**: Full library contract coverage for `RESISTOR`, `CAPACITOR`, `INDUCTOR`, `DIODE`, `LED`, `NPN`, `PNP`, `NMOS`, `PMOS`, `OPAMP`, `CONNECTOR`, `GROUND`, `VCC`.
- **Two Export Modes**:
  - **Mode A (Stub + Net Alias)**: Robust placement with short orthogonal stubs and net aliases. Capture connects same-named nets on a sheet.
  - **Mode B (Routed Polylines)**: Directly connects pin ends and junctions using orthogonal L-bends.
- **Formalized Confidence Scoring**: Weighted formula based on symbol detection confidence (35%), OCR confidence (25%), pin connectivity (25%), and net completeness (15%) minus ERC penalties.
- **Automated Round-Trip Proof**: Converts IR and Capture netlists into canonical partition sets (`frozenset` of `frozenset` of `(refdes, pin)`), mathematically verifying 100% netlist equivalence.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/JatinMakhija-10/Schematic2DSN.git
cd Schematic2DSN
```

### 2. Environment Setup
```bash
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate

# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the End-to-End Pipeline
```bash
# Process a schematic PDF or image
python -m core.pipeline input_schematic.pdf out/

# Export using Mode B (routed polylines)
python -m core.pipeline input_schematic.png out/ --mode-b
```

### 4. Launch the Interactive Streamlit Web App
```bash
streamlit run app/streamlit_app.py
```
Open your browser at `http://localhost:8501` to access:
- Multi-layer debug vision overlays (Original, Text, Wires, Symbols, Junctions)
- Interactive IR tree inspector with instant `design.json` downloads
- Live ERC validation report and component summary tables
- One-click Tcl script generation and download
- Built-in ground-truth circuit benchmark loader

---

## 📦 Stage CLI Reference

Every stage in Schematic2DSN is a pure, deterministic function with its own CLI:

| Stage | Module | CLI Command | Output Artifact |
|---|---|---|---|
| **S1 Ingest** | `vision.ingest` | `python -m vision.ingest in.pdf out/` | `page.png`, `page.meta.json` |
| **S2 Text** | `vision.ocr` | `python -m vision.ocr in/page.png out/` | `texts.json`, `debug/ocr.png` |
| **S2+S4 Vector** | `vision.vector_extract` | `python -m vision.vector_extract in.pdf meta.json out/` | `texts.json`, `wires.json` |
| **S3 Symbols** | `vision.symbols_cv` | `python -m vision.symbols_cv in/page.png in/texts.json out/` | `symbols.json`, `debug/symbols_cv.png` |
| **S4 Wires** | `vision.wires` | `python -m vision.wires in/page.png in/symbols.json in/texts.json out/` | `wires.json`, `debug/wires.png` |
| **S5 Junctions** | `vision.junctions` | `python -m vision.junctions in/page.png in/wires.json out/` | `junctions.json`, `debug/junctions.png` |
| **S7 Graph** | `circuit.graph` | `python -m circuit.graph in/wires.json in/junctions.json out/` | `nets_raw.json` |
| **S8 Associate** | `circuit.associate` | `python -m circuit.associate in/symbols.json in/texts.json out/` | `components_raw.json` |
| **S10 Export** | `orcad.tcl_gen` | `python -m orcad.tcl_gen in/design.json out/design.tcl` | `design.tcl` |
| **S11 Round-Trip** | `orcad.roundtrip` | `python -m orcad.roundtrip in/design.json in/netlist.txt` | Comparison Report |

---

## 🧪 Benchmark Circuits Suite

The repository includes 9 golden reference circuits with verified ground-truth netlists:

1. **Voltage Divider**: Resistor divider `VCC -> R1 -> R2 -> GND`.
2. **RC Low-Pass Filter**: `VCC -> R1 -> OUT -> C1 -> GND`.
3. **LED Driver**: Current-limiting resistor with red indicator LED.
4. **Inverting Op-Amp**: Classic operational amplifier with input and feedback resistors.
5. **Common Emitter**: BJT transistor amplifier stage with collector load and base bias.
6. **BJT Astable Multivibrator**: Dual transistor cross-coupled square-wave oscillator.
7. **H-Bridge Motor Driver**: 4 MOSFET power stage controlling a terminal connector.
8. **Differential Amplifier**: Balanced op-amp stage with matched precision resistor network.
9. **RLC Bandpass Filter**: Second-order passive filter (`R1`, `L1`, `C1`).

Generate all synthetic benchmarks at any time:
```bash
python -m data.synthetic.generate_test_circuits
```

---

## 🔬 Testing & Continuous Integration

All 151+ test cases run with `pytest` and execute in under 7 seconds:

```bash
pytest -v
```

```text
============================= test session starts =============================
collected 151 items

tests/test_associate.py ...                                              [  2%]
tests/test_circuits_extended.py ....                                     [  4%]
tests/test_confidence.py ...                                             [  6%]
tests/test_frontend.py ......                                            [ 10%]
tests/test_geometry.py ..............                                    [ 19%]
tests/test_golden.py ..................                                  [ 31%]
tests/test_graph.py ....                                                 [ 34%]
tests/test_ingest.py ......                                              [ 38%]
tests/test_junctions.py ....                                             [ 40%]
tests/test_ocr.py .......                                                [ 45%]
tests/test_pins.py .....                                                 [ 48%]
tests/test_pipeline.py ..                                                [ 50%]
tests/test_pipeline_e2e.py ..                                            [ 51%]
tests/test_roundtrip.py ..............................                   [ 71%]
tests/test_symbols_cv.py ......                                          [ 75%]
tests/test_symbols_yolo.py ..                                            [ 76%]
tests/test_tcl_gen.py ...........                                        [ 84%]
tests/test_units.py ........                                             [ 89%]
tests/test_validate.py .....                                             [ 92%]
tests/test_vector_extract.py ......                                      [ 96%]
tests/test_wires.py .....                                                [100%]

============================= 151 passed in 5.67s =============================
```

---

## 👤 Author & Maintainer

**Jatin Makhija**
- **GitHub**: [@JatinMakhija-10](https://github.com/JatinMakhija-10)
- **Repository**: [https://github.com/JatinMakhija-10/Schematic2DSN](https://github.com/JatinMakhija-10/Schematic2DSN)
- **Email**: [jatinmakhija2007@gmail.com](mailto:jatinmakhija2007@gmail.com)

Contributions, feature requests, and feedback are welcome! Please check the [Contributing Guidelines](CONTRIBUTING.md) or open an [Issue](https://github.com/JatinMakhija-10/Schematic2DSN/issues).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
