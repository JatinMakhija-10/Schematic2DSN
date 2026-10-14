"""
generate_whitepaper.py
Generates the comprehensive Schematic2DSN Technology & Architecture Whitepaper as a multi-page PDF.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import pymupdf
from pathlib import Path

def generate_pdf(output_path: str = "Schematic2DSN_Technology_Whitepaper.pdf"):
    doc = pymupdf.open()
    
    # Global CSS
    css = """
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 9pt;
        line-height: 1.38;
        color: #1e293b;
    }
    h1 {
        font-size: 19pt;
        color: #0f172a;
        margin: 0 0 4px 0;
        font-weight: bold;
    }
    h2 {
        font-size: 11.5pt;
        color: #0369a1;
        border-bottom: 1.5px solid #0284c7;
        padding-bottom: 3px;
        margin: 12px 0 6px 0;
        font-weight: bold;
    }
    h3 {
        font-size: 9.5pt;
        color: #0f172a;
        margin: 8px 0 3px 0;
        font-weight: bold;
    }
    p {
        margin: 4px 0;
    }
    .subtitle {
        color: #0284c7;
        font-size: 9pt;
        font-weight: bold;
        margin-bottom: 6px;
    }
    .author-bar {
        background: #0f172a;
        color: #f8fafc;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 8pt;
        margin-bottom: 10px;
    }
    .author-bar a {
        color: #38bdf8;
        text-decoration: none;
    }
    .highlight-card {
        background: #f0f9ff;
        border-left: 4px solid #0284c7;
        padding: 6px 10px;
        margin: 7px 0;
        font-size: 8.5pt;
    }
    .stage-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3.5px solid #0ea5e9;
        padding: 5px 8px;
        margin: 5px 0;
        border-radius: 3px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 6px 0;
        font-size: 7.8pt;
    }
    th {
        background: #0284c7;
        color: white;
        padding: 4px 6px;
        text-align: left;
        font-weight: bold;
    }
    td {
        border: 1px solid #cbd5e1;
        padding: 3.5px 5px;
        vertical-align: top;
    }
    tr:nth-child(even) {
        background: #f8fafc;
    }
    .badge {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        padding: 1px 4px;
        border-radius: 3px;
        font-weight: bold;
        font-size: 7.5pt;
    }
    .footer {
        position: absolute;
        bottom: 25px;
        left: 40px;
        right: 40px;
        font-size: 7pt;
        color: #64748b;
        border-top: 1px solid #cbd5e1;
        padding-top: 4px;
        text-align: center;
    }
    """

    # -------------------------------------------------------------------------
    # PAGE 1: Overview & Executive Summary
    # -------------------------------------------------------------------------
    html_page1 = """
    <h1>⚡ Schematic2DSN: Technical Architecture & Solution</h1>
    <div class="subtitle">Automated Circuit Graph Reconstruction & Cadence OrCAD Compiler</div>
    <div class="author-bar">
        Developed by <b>Jatin Makhija</b> (@JatinMakhija-10) &bull; Repository: github.com/JatinMakhija-10/Schematic2DSN &bull; Python 3.11+ &bull; 163 Tests Passing
    </div>

    <div class="highlight-card">
        <b>The Core Engineering Thesis:</b> We do not simply draw a picture or produce a flat raster replica of a schematic; we reconstruct the underlying circuit topology graph and compile it into a native, fully editable, journal-verified Cadence OrCAD Capture design (.DSN) placed on the 100-mil electrical snap grid.
    </div>

    <h2>1. The Problem: Legacy Schematic Lock-In</h2>
    <p>Millions of mission-critical electrical designs exist only as static PDFs, scanned blueprints, or legacy image archives. Engineers needing to modify, simulate, or fabricate these circuits face hours or days of error-prone manual labor in EDA software: manually redrawing symbols, reconnecting every pin, and re-typing labels.</p>
    <p>Existing optical approaches fail because standard OCR/computer vision outputs dumb pixels. Circuit simulation and PCB layout require <b>strict topological netlists</b>, where pin numbers govern physical connectivity and wires snap to a discrete 100-mil grid.</p>

    <h2>2. End-to-End Compiler Architecture</h2>
    <p>Schematic2DSN operates as a deterministic 11-stage compiler pipeline. Every stage reads and writes verified Pydantic JSON contracts, allowing pure-function modularity and rigorous unit testing:</p>

    <table>
        <tr>
            <th style="width:14%;">Stage</th>
            <th style="width:26%;">Module</th>
            <th style="width:30%;">Input & Output Contract</th>
            <th style="width:30%;">Key Engineering Function</th>
        </tr>
        <tr>
            <td><b>S1 Ingest</b></td>
            <td><code>vision.ingest</code></td>
            <td>PDF/PNG &rarr; <code>page.png</code>, <code>page.meta.json</code></td>
            <td>Dual-pathway vector/raster routing, skew correction, DPI checks</td>
        </tr>
        <tr>
            <td><b>S2 Text</b></td>
            <td><code>vision.ocr</code></td>
            <td><code>page.png</code> &rarr; <code>texts.json</code></td>
            <td>0&deg;/90&deg; RapidOCR sweeps + electronic regex normalization</td>
        </tr>
        <tr>
            <td><b>S3 Symbols</b></td>
            <td><code>vision.symbols_cv</code></td>
            <td><code>page.png</code> &rarr; <code>symbols.json</code></td>
            <td>Text masking + geometric heuristics (13 classes) + YOLOv8</td>
        </tr>
        <tr>
            <td><b>S4 Wires</b></td>
            <td><code>vision.wires</code></td>
            <td><code>page.png</code> &rarr; <code>wires.json</code></td>
            <td>Symbol masking + medial axis skeletonization + Hough transform</td>
        </tr>
        <tr>
            <td><b>S5 Junctions</b></td>
            <td><code>vision.junctions</code></td>
            <td><code>page.png</code> &rarr; <code>junctions.json</code></td>
            <td>Morphological disk opening (circularity &gt; 0.7) for solder dots</td>
        </tr>
        <tr>
            <td><b>S6 Pins</b></td>
            <td><code>vision.pins</code></td>
            <td><code>symbols.json</code> &rarr; <code>pins.json</code></td>
            <td>Rigid EDA library offsets snapped to wire endpoints (&le; 6px)</td>
        </tr>
        <tr>
            <td><b>S7 Graph</b></td>
            <td><code>circuit.graph</code></td>
            <td>Wires/Junctions &rarr; <code>nets_raw.json</code></td>
            <td>Union-Find (DSU) engine + global net alias label propagation</td>
        </tr>
        <tr>
            <td><b>S8 Associate</b></td>
            <td><code>circuit.associate</code></td>
            <td>Texts/Symbols &rarr; <code>components_raw.json</code></td>
            <td>Bipartite Hungarian optimization for RefDes and values</td>
        </tr>
        <tr>
            <td><b>S9 Validate</b></td>
            <td><code>circuit.validate</code></td>
            <td>Raw Graph &rarr; <code>design.json</code> (IR)</td>
            <td>Electrical Rules Check (ERC) + deterministic confidence score</td>
        </tr>
        <tr>
            <td><b>S10 Export</b></td>
            <td><code>orcad.tcl_gen</code></td>
            <td><code>design.json</code> &rarr; <code>design.tcl</code></td>
            <td>100-mil grid compile: Mode A (stubs) or Mode B (polylines)</td>
        </tr>
        <tr>
            <td><b>S11 Roundtrip</b></td>
            <td><code>orcad.roundtrip</code></td>
            <td><code>design.json</code> + Netlist &rarr; Proof</td>
            <td>Canonical partition equivalence proof (frozenset of frozenset)</td>
        </tr>
    </table>
    """

    # -------------------------------------------------------------------------
    # PAGE 2: Vision & Extraction Pipeline
    # -------------------------------------------------------------------------
    html_page2 = """
    <h2>3. The Vision & Topological Extraction Engine</h2>
    
    <div class="stage-card">
        <h3>Stage 1: Dual-Pathway Ingest (Vector vs. Raster)</h3>
        <p><b>Vector Pathway:</b> When processing vector PDFs, Schematic2DSN inspects internal drawing streams with PyMuPDF (<code>get_drawings()</code> and <code>get_text("dict")</code>). This extracts mathematically exact line endpoints and text characters directly from the file, bypassing raster distortion entirely.</p>
        <p><b>Raster Pathway:</b> For scans or photos, it renders at 600 DPI, runs Otsu adaptive thresholding, removes speckles (&lt;6 px area), and deskews using dominant Hough angles. Rejection rules immediately flag multi-page PDFs, low resolution (&lt;1200 px long side), or excessive line skew.</p>
    </div>

    <div class="stage-card">
        <h3>Stage 2: Text Extraction & Domain Regex Normalization</h3>
        <p>Schematic labels are often vertical. The OCR engine executes dual 0&deg; and 90&deg; sweeps with ONNX-accelerated RapidOCR, merging overlaps by confidence. Crucially, raw strings pass through domain-specific regex normalizers:</p>
        <ul>
            <li><b>RefDes Repair:</b> Fixes optical character ambiguities (e.g., <code>RI</code> &rarr; <code>R1</code>, <code>QO</code> &rarr; <code>Q0</code>, <code>CI</code> &rarr; <code>C1</code>) according to standard electronics prefixes.</li>
            <li><b>Engineering Unit Normalization:</b> Converts shorthand notation: <code>4k7</code> &rarr; <code>4.7k</code>, <code>100R</code> &rarr; <code>100ohm</code>, <code>.1uF</code> &rarr; <code>0.1uF</code>, <code>10K</code> &rarr; <code>10k</code>.</li>
            <li><b>Net Alias Detection:</b> Maps standard power and control rails: <code>VCC</code>, <code>GND</code>, <code>+5V</code>, <code>3V3</code>, <code>RESET</code>, <code>SCL</code>, <code>SDA</code>.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 3: Symbol Detection & Classification</h3>
        <p>Text bounding boxes are dilated and subtracted first, ensuring text characters are never mistaken for circuit shapes. A hybrid engine classifies 13 component types (Resistors, Capacitors, Inductors, Diodes, LEDs, BJTs, MOSFETs, Op-Amps, Connectors, Ground, VCC):</p>
        <ul>
            <li><b>Geometric Heuristics (CV):</b> Resistors are identified by zig-zag turns (&ge;6) or IEC rectangles; Capacitors by parallel dielectric plates; Diodes/LEDs by triangles touching a cathode bar; Op-amps by triangular dual-input bodies.</li>
            <li><b>YOLOv8 Detection:</b> Deep learning model trained on synthesized multi-rotation symbol datasets.</li>
            <li><b>Orientation & Polarity:</b> Computes rotation (0&deg;, 90&deg;, 180&deg;, 270&deg;) and mirror status from physical asymmetry.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 4 & 5: Wire Segmentation & Solder Dot Classification</h3>
        <p><b>Solder Dot Opening:</b> Morphological opening with a circular structuring element larger than wire width erases thin lines and isolates solder dots. Connected components with circularity &gt; 0.70 are registered as junctions.</p>
        <p><b>Electronics Connectivity Rules:</b></p>
        <ul>
            <li><b>4-Way Cross (+) without Dot:</b> Independent wire jumper (NOT connected).</li>
            <li><b>4-Way Cross (+) with Solder Dot:</b> Bonded 4-way node (CONNECTED).</li>
            <li><b>3-Way T-Junction (&top;):</b> Always an electrical connection (CONNECTED).</li>
        </ul>
    </div>
    """

    # -------------------------------------------------------------------------
    # PAGE 3: Circuit Graph & Optimization
    # -------------------------------------------------------------------------
    html_page3 = """
    <h2>4. Graph Reconstruction, Association & Validation</h2>

    <div class="stage-card">
        <h3>Stage 6: EDA Library Contract & Pin Snapping</h3>
        <p>In electronic engineering, pin locations are strictly defined by library geometry, not by image artifacts. Schematic2DSN maintains an exact library contract in <code>orcad/symbols.json</code>. For a detected symbol at $(x, y)$ with rotation &theta;, theoretical pin terminal coordinates are calculated and snapped to the nearest extracted wire endpoint within a calibrated 6-pixel threshold. Pins lacking attached wires are marked as <code>UNCONNECTED_PIN</code>.</p>
    </div>

    <div class="stage-card">
        <h3>Stage 7: Union-Find (DSU) Electrical Net Extraction</h3>
        <p>Wire segments, solder junctions, component pins, and net label markers form an undirected graph $G = (V, E)$. The system executes a Disjoint-Set Union (Union-Find) algorithm with path compression and union-by-rank:</p>
        <ul>
            <li>Every connected cluster of segments and pins collapses into a single <b>Electrical Net</b>.</li>
            <li>Identically named net aliases (e.g. <code>VCC</code>, <code>GND</code>, <code>RESET</code>) globally merge separated net sets.</li>
            <li>Nets are automatically assigned canonical deterministic identifiers (<code>NET_001</code>, <code>NET_002</code>) or preserve explicit label names.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 8: Bipartite Matching via the Hungarian Algorithm</h3>
        <p>Associating free-floating text labels with nearby component symbols is modeled as a <b>Minimum-Weight Bipartite Matching Problem</b>. A global cost matrix is computed based on Euclidean distance, orientation alignment, and prefix compatibility ($R \rightarrow \text{Resistor}$, $C \rightarrow \text{Capacitor}$):</p>
        <p style="text-align: center; font-style: italic; margin: 4px 0;">Cost = Distance + Prefix_Penalty + Orientation_Penalty</p>
        <p>Solved using the Kuhn-Munkres (Hungarian) algorithm (<code>scipy.optimize.linear_sum_assignment</code>), ensuring each component receives its mathematically optimal RefDes and value without duplicates.</p>
    </div>

    <div class="stage-card">
        <h3>Stage 9: Electrical Rules Check (ERC) & Confidence Scoring</h3>
        <p>Before compilation, the intermediate representation (<code>design.json</code>) undergoes automated Electrical Rules Checking:</p>
        <ul>
            <li>Checks for dangling single-pin nets, unconnected component pins, and duplicate RefDes.</li>
            <li>Flags floating active inputs and missing passive values.</li>
        </ul>
        <p><b>Deterministic Confidence Formula:</b> Confidence is mathematically derived rather than guessed by an LLM:</p>
        <p style="background:#e0f2fe; padding:4px 8px; border-radius:3px; font-size:8pt; font-family:monospace;">
            Confidence = 0.35 &times; C_symbols + 0.25 &times; C_ocr + 0.25 &times; (Connected_Pins / Total_Pins) + 0.15 &times; (Valid_Nets / Total_Nets) - &Sigma; Penalties
        </p>
    </div>
    """

    # -------------------------------------------------------------------------
    # PAGE 4: Cadence Compiler, Roundtrip Proof & Web Platform
    # -------------------------------------------------------------------------
    html_page4 = """
    <h2>5. Cadence OrCAD Compiler & Automated Round-Trip Proof</h2>

    <div class="stage-card">
        <h3>Stage 10: Cadence OrCAD Capture Tcl Generation</h3>
        <p>Schematic2DSN translates the intermediate representation into clean, journal-verified Cadence Capture Tcl scripts:</p>
        <ul>
            <li><b>Grid Snapping:</b> Image coordinates ($Y$-down) are converted to OrCAD mils ($Y$-up) and snapped to Cadence's strict <b>100-mil electrical snap grid</b>.</li>
            <li><b>Mode A (Stub + Net Alias &mdash; Robust):</b> Places components, draws short orthogonal stubs from each pin, and attaches net aliases. OrCAD Capture natively bonds same-named aliases on the sheet. Highly robust and 100% editable.</li>
            <li><b>Mode B (Routed Polylines &mdash; Geometric):</b> Renders full orthogonal routed wire polylines matching original schematic visual paths.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 11: Canonical Netlist Round-Trip Proof</h3>
        <p>To mathematically prove that the generated design matches the input schematic without human bias:</p>
        <ol>
            <li>The generated Tcl script is sourced in OrCAD Capture to build the native <code>.DSN</code> database.</li>
            <li>Capture dumps its generated netlist.</li>
            <li>Schematic2DSN parses both the input IR and the Capture netlist into <b>Canonical Partition Sets</b>:
                <br><code>S = frozenset( frozenset((refdes, pin_number), ...) )</code>
            </li>
            <li>An automated set-equality check validates <b>100% topological equivalence</b>.</li>
        </ol>
    </div>

    <h2>6. Interactive Streamlit Web Platform & Cloud Infrastructure</h2>
    <p>Schematic2DSN provides an engineer-friendly Streamlit web interface with real-time feedback:</p>
    <ul>
        <li><b>Multi-Layer Vision Overlay:</b> Toggle between Raw Image, Text OCR, Wire Skeletons, Detected Symbols, and Solder Junctions.</li>
        <li><b>Live IR Inspector & Tcl Downloader:</b> Immediate JSON tree inspector, ERC warning logs, and one-click <code>design.tcl</code> download.</li>
        <li><b>Cloud Resilience:</b> Fully configured with <code>packages.txt</code> (providing <code>libgl1</code> and <code>libglib2.0-0</code>) to ensure headless Linux execution on Streamlit Community Cloud and Docker containers without graphics library failures.</li>
    </ul>

    <h2>7. Quality Assurance & Test Metrics</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
            <th>Verification Method</th>
        </tr>
        <tr><td>Automated Test Suite</td><td><b>163 Unit & Integration Tests Passing</b></td><td><code>pytest -v</code> in 6.2 seconds</td></tr>
        <tr><td>Benchmark Circuits Suite</td><td><b>12 Reference Ground-Truth Circuits</b></td><td>Synthetic and golden reference schematics</td></tr>
        <tr><td>Coordinate Grid Accuracy</td><td><b>100% Snap on 100-mil Grid</b></td><td>Verified in Cadence OrCAD Capture</td></tr>
        <tr><td>Component Coverage</td><td><b>13 Electrical Symbol Classes</b></td><td>Passives, Discretes, ICs, Power Rails</td></tr>
    </table>
    """

    # -------------------------------------------------------------------------
    # PAGE 5: Benchmark Circuits Reference Table
    # -------------------------------------------------------------------------
    html_page5 = """
    <h2>8. Benchmark Circuits Suite (Ready-to-Test PDFs)</h2>
    <p>The repository contains 12 verified reference circuits with ground-truth netlists, available in <code>data/synthetic/</code> and <code>sample_schematics/</code>:</p>

    <table>
        <tr>
            <th style="width:25%;">Circuit Benchmark</th>
            <th style="width:25%;">Components Included</th>
            <th style="width:50%;">Electrical Capabilities Tested</th>
        </tr>
        <tr>
            <td><b>Voltage Divider</b></td>
            <td>R1, R2, VCC, GND</td>
            <td>Symmetric passive divider chain, vertical rail connection, baseline test</td>
        </tr>
        <tr>
            <td><b>RC Low-Pass Filter</b></td>
            <td>R1, C1, VCC, GND, OUT</td>
            <td>Resistor-capacitor filtering, ground connection, output node extraction</td>
        </tr>
        <tr>
            <td><b>LED Driver</b></td>
            <td>R1, D1 (LED), VCC, GND</td>
            <td>Diode polarity verification, current limiter passive, cathode-anode assignment</td>
        </tr>
        <tr>
            <td><b>Inverting Op-Amp</b></td>
            <td>U1, R1, R2, VCC, VEE</td>
            <td>5-pin active op-amp symbol, input resistor, feedback loop, dual power rails</td>
        </tr>
        <tr>
            <td><b>BJT Common Emitter</b></td>
            <td>Q1 (NPN), R1, R2, RC, RE, VCC</td>
            <td>Bipolar transistor terminals (Base, Collector, Emitter), bias network</td>
        </tr>
        <tr>
            <td><b>BJT Astable Multivibrator</b></td>
            <td>Q1, Q2, R1-R4, C1-C2, VCC</td>
            <td>Cross-coupled symmetric oscillator, 4-way wire crossings, solder junctions</td>
        </tr>
        <tr>
            <td><b>H-Bridge Motor Driver</b></td>
            <td>M1-M4 (MOSFETs), J1, VCC</td>
            <td>4-MOSFET power bridge, Gate-Drain-Source snapping, terminal connector</td>
        </tr>
        <tr>
            <td><b>Differential Amplifier</b></td>
            <td>U1, R1-R4, VCC, VEE</td>
            <td>Balanced precision instrumentation stage, matched resistor network</td>
        </tr>
        <tr>
            <td><b>RLC Bandpass Filter</b></td>
            <td>R1, L1, C1, GND</td>
            <td>Second-order passive filter including inductor coil symbol extraction</td>
        </tr>
        <tr>
            <td><b>NE555 Timer Astable</b></td>
            <td>U1 (8-pin IC), R1, R2, C1</td>
            <td>Complex multi-pin IC: VCC, GND, TRIG, OUT, RESET, CONT, THRES, DISCH</td>
        </tr>
        <tr>
            <td><b>LM2596 Buck Regulator</b></td>
            <td>U1 (5-pin), L1, D1, C1, C2</td>
            <td>Switching power supply topology, Schottky catch diode, power inductor</td>
        </tr>
        <tr>
            <td><b>ATmega328P MCU System</b></td>
            <td>U1 (28/32-pin), XTAL, C1-C3</td>
            <td>High pin-count microcontroller, crystal oscillator tank, bypass passives</td>
        </tr>
    </table>

    <h2>9. How to Run & Verify Live</h2>
    <div class="stage-card">
        <h3>1. Run the Entire Test Suite</h3>
        <p><code>pytest -v</code> &mdash; Executes all 163 unit and integration tests across all compiler stages in &lt;7 seconds.</p>
        <h3>2. Run CLI Pipeline on Any Benchmark PDF</h3>
        <p><code>python -m core.pipeline sample_schematics/voltage_divider.pdf out/ --generate-tcl</code></p>
        <h3>3. Launch Web Platform</h3>
        <p><code>streamlit run app/streamlit_app.py</code> &mdash; Open http://localhost:8501 and upload any schematic PDF from <code>sample_schematics/</code>.</p>
    </div>

    <div class="highlight-card" style="margin-top: 15px; text-align: center;">
        <b>Schematic2DSN &bull; Developed by Jatin Makhija (@JatinMakhija-10)</b><br>
        Source Code: <a href="https://github.com/JatinMakhija-10/Schematic2DSN">https://github.com/JatinMakhija-10/Schematic2DSN</a>
    </div>
    """

    pages_content = [html_page1, html_page2, html_page3, html_page4, html_page5]
    
    for i, content in enumerate(pages_content):
        page = doc.new_page(width=595, height=842) # A4
        rect = pymupdf.Rect(38, 38, 595 - 38, 842 - 38)
        page.insert_htmlbox(rect, content, css=css)
        
        # Add footer with page number
        footer_text = f"Schematic2DSN Technical Whitepaper &bull; Author: Jatin Makhija &bull; Page {i+1} of {len(pages_content)}"
        page.insert_text(pymupdf.Point(595/2 - 140, 842 - 20), footer_text, fontsize=7.5, color=(0.4, 0.45, 0.5))

    doc.save(output_path)
    doc.close()
    print(f"Successfully generated whitepaper at: {output_path} ({len(pages_content)} pages)")

if __name__ == "__main__":
    generate_pdf()
