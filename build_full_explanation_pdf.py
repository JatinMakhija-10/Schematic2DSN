"""
build_full_explanation_pdf.py
Generates the complete, dedicated PDF document of the entire Schematic2DSN technology explanation.
Author: Jatin Makhija (@JatinMakhija-10)
"""
import pymupdf
import shutil
from pathlib import Path

def generate_pdf():
    doc = pymupdf.open()

    css = """
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 8.8pt;
        line-height: 1.35;
        color: #1e293b;
    }
    h1 {
        font-size: 18pt;
        color: #0f172a;
        margin: 0 0 3px 0;
        font-weight: bold;
    }
    h2 {
        font-size: 11pt;
        color: #0284c7;
        border-bottom: 1.5px solid #0284c7;
        padding-bottom: 2px;
        margin: 10px 0 5px 0;
        font-weight: bold;
    }
    h3 {
        font-size: 9pt;
        color: #0f172a;
        margin: 6px 0 2px 0;
        font-weight: bold;
    }
    p {
        margin: 3px 0;
    }
    ul, ol {
        margin: 3px 0 3px 14px;
        padding: 0;
    }
    li {
        margin-bottom: 2px;
    }
    .subtitle {
        color: #0369a1;
        font-size: 9pt;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .author-bar {
        background: #0f172a;
        color: #f8fafc;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 7.8pt;
        margin-bottom: 8px;
    }
    .highlight-card {
        background: #f0f9ff;
        border-left: 4px solid #0284c7;
        padding: 6px 10px;
        margin: 6px 0;
        font-size: 8.4pt;
        border-radius: 2px;
    }
    .stage-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3.5px solid #0ea5e9;
        padding: 5px 8px;
        margin: 4px 0;
        border-radius: 3px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 5px 0;
        font-size: 7.5pt;
    }
    th {
        background: #0284c7;
        color: white;
        padding: 4px 5px;
        text-align: left;
        font-weight: bold;
    }
    td {
        border: 1px solid #cbd5e1;
        padding: 3px 5px;
        vertical-align: top;
    }
    tr:nth-child(even) {
        background: #f8fafc;
    }
    code {
        font-family: monospace;
        background: #e2e8f0;
        padding: 1px 3px;
        border-radius: 2px;
        font-size: 8pt;
    }
    .formula-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 5px 8px;
        border-radius: 3px;
        font-family: monospace;
        font-size: 7.8pt;
        margin: 4px 0;
    }
    """

    # -------------------------------------------------------------------------
    # PAGE 1: Title, Executive Summary, The Problem & The 11-Stage Architecture
    # -------------------------------------------------------------------------
    page1_html = """
    <h1>⚡ Schematic2DSN: Complete Technology & Solution Guide</h1>
    <div class="subtitle">Automated Circuit Graph Reconstruction & Cadence OrCAD Compiler</div>
    <div class="author-bar">
        Developed by <b>Jatin Makhija</b> (@JatinMakhija-10) &bull; Repository: https://github.com/JatinMakhija-10/Schematic2DSN &bull; Python 3.11+ &bull; 163 Tests Passing
    </div>

    <div class="highlight-card">
        <b>The Core Engineering Thesis:</b> We do not simply draw a picture or produce a flat raster replica of a schematic; we reconstruct the underlying circuit topology graph and compile it into a native, fully editable, journal-verified Cadence OrCAD Capture design (.DSN) placed on the 100-mil electrical snap grid.
    </div>

    <h2>1. Executive Summary & The Problem It Solves</h2>
    <p><b>The Industry Challenge:</b> Millions of mission-critical electrical designs exist only as static PDFs, scanned blueprints, or legacy image archives. Engineers needing to modify, simulate, or fabricate these circuits face hours or days of error-prone manual labor in EDA software: manually redrawing symbols, reconnecting every pin, and re-typing labels. Optical approaches that simply vectorize pixels fail because circuit simulation and PCB manufacturing require <b>strict topological netlists</b>, where pin numbers govern physical connectivity and wires snap to a discrete 100-mil grid.</p>
    <p><b>The Schematic2DSN Solution:</b> Schematic2DSN is an end-to-end compiler that deconstructs visual schematics, extracts electrical primitives, builds a formal graph using Union-Find, runs Electrical Rules Checking (ERC), and compiles journal-verified Cadence Tcl scripts that produce ready-to-simulate OrCAD designs.</p>

    <h2>2. High-Level Architecture: The 11-Stage Compiler</h2>
    <p>Every stage reads and writes verified Pydantic JSON contracts, allowing pure-function modularity and rigorous unit testing:</p>

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
    # PAGE 2: Vision & Extraction Pipeline (S1 to S5)
    # -------------------------------------------------------------------------
    page2_html = """
    <h2>3. Deep Dive into the 11 Pipeline Stages: Vision & Extraction</h2>

    <div class="stage-card">
        <h3>Stage 1: Dual-Pathway Ingest & Skew Correction (<code>vision.ingest</code>)</h3>
        <p><b>Vector Pathway:</b> When processing vector PDFs, the system uses PyMuPDF (<code>get_drawings()</code> and <code>get_text("dict")</code>) to extract line coordinates and font glyphs directly from the document's internal display list. This provides mathematically exact lines with zero raster noise.</p>
        <p><b>Raster Pathway:</b> Scanned images are rendered at 600 DPI, processed with Otsu adaptive thresholding, filtered to remove speckles (&lt;6 px area), and deskewed using dominant Hough angles. Gatekeeping rules immediately reject multi-page files, low resolution (&lt;1200 px long side), or excessive line skew with machine-readable rejection codes.</p>
    </div>

    <div class="stage-card">
        <h3>Stage 2: Text Extraction & Electronics Regex Normalization (<code>vision.ocr</code>)</h3>
        <p>Schematic labels are frequently rotated. The engine executes dual 0&deg; and 90&deg; sweeps using ONNX-accelerated RapidOCR, merging overlapping bounding boxes by confidence. Crucially, raw strings are post-processed with domain-specific electronics regexes:</p>
        <ul>
            <li><b>RefDes Repair:</b> Corrects character ambiguities (e.g. <code>RI</code> &rarr; <code>R1</code>, <code>QO</code> &rarr; <code>Q0</code>, <code>CI</code> &rarr; <code>C1</code>) according to standard engineering prefixes.</li>
            <li><b>Engineering Unit Normalization:</b> Converts shorthand notation: <code>4k7</code> &rarr; <code>4.7k</code>, <code>100R</code> &rarr; <code>100ohm</code>, <code>.1uF</code> &rarr; <code>0.1uF</code>, <code>10K</code> &rarr; <code>10k</code>.</li>
            <li><b>Net Alias Detection:</b> Identifies power, ground, and control nets: <code>VCC</code>, <code>GND</code>, <code>+5V</code>, <code>3V3</code>, <code>RESET</code>, <code>SCL</code>, <code>SDA</code>.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 3: Symbol Detection & Classification (<code>vision.symbols_cv</code>)</h3>
        <p>Text bounding boxes are dilated and subtracted first, preventing letters from being mistaken for circuit shapes. A hybrid engine classifies 13 component types (Resistors, Capacitors, Inductors, Diodes, LEDs, BJTs, MOSFETs, Op-Amps, Connectors, Ground, VCC):</p>
        <ul>
            <li><b>Geometric Computer Vision:</b> Resistors are identified by zig-zag turns (&ge;6) or IEC rectangles; Capacitors by parallel dielectric plates; Diodes/LEDs by triangles touching a cathode bar; Op-amps by triangular dual-input bodies.</li>
            <li><b>YOLOv8 Detection:</b> Deep learning model trained on synthesized multi-rotation symbol datasets.</li>
            <li><b>Orientation & Polarity:</b> Computes rotation (0&deg;, 90&deg;, 180&deg;, 270&deg;) and mirror status from physical asymmetry.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 4 & 5: Wire Segmentation & Solder Dot Classification (<code>vision.wires</code>, <code>vision.junctions</code>)</h3>
        <p><b>Wire Extraction:</b> Symbol bounding boxes are masked out so internal component features are not extracted as wires. The image is skeletonized to a 1-pixel medial axis, vectorized with Hough transforms, snapped to 0&deg;/90&deg;, and split at T-junctions.</p>
        <p><b>Solder Dot Opening:</b> Morphological opening with a circular structuring element larger than wire width erases thin lines, leaving only solid solder blobs. Connected components with circularity &gt; 0.70 are registered as junctions.</p>
        <p><b>Electronics Connectivity Rules:</b></p>
        <ul>
            <li><b>4-Way Cross (+) without Dot:</b> Independent wire jumper (NOT connected).</li>
            <li><b>4-Way Cross (+) with Solder Dot:</b> Bonded 4-way node (CONNECTED).</li>
            <li><b>3-Way T-Junction (&top;):</b> Always an electrical connection (CONNECTED).</li>
        </ul>
    </div>
    """

    # -------------------------------------------------------------------------
    # PAGE 3: Graph Reconstruction & Validation (S6 to S9)
    # -------------------------------------------------------------------------
    page3_html = """
    <h2>3. Deep Dive (Cont.): Graph Reconstruction, Association & Validation</h2>

    <div class="stage-card">
        <h3>Stage 6: Rigid EDA Library Contract & Pin Snapping (<code>vision.pins</code>)</h3>
        <p>In electronic engineering, pin locations are strictly defined by library geometry, not by image artifacts. Schematic2DSN maintains an exact library contract in <code>orcad/symbols.json</code> matching standard Cadence libraries. For a detected symbol at $(x, y)$ with rotation &theta;, theoretical pin terminal coordinates are calculated and snapped to the nearest extracted wire endpoint within a calibrated 6-pixel threshold. Pins lacking attached wires are marked as <code>UNCONNECTED_PIN</code>.</p>
    </div>

    <div class="stage-card">
        <h3>Stage 7: Union-Find (DSU) Electrical Net Extraction (<code>circuit.graph</code>)</h3>
        <p>Wire segments, solder junctions, component pins, and net label markers form an undirected graph $G = (V, E)$. The system executes a Disjoint-Set Union (Union-Find) algorithm with path compression and union-by-rank:</p>
        <ul>
            <li>Every connected cluster of segments and pins collapses into a single <b>Electrical Net</b>.</li>
            <li>Identically named net aliases (e.g. <code>VCC</code>, <code>GND</code>, <code>RESET</code>) globally merge separated net sets.</li>
            <li>Nets are automatically assigned canonical deterministic identifiers (<code>NET_001</code>, <code>NET_002</code>) or preserve explicit label names.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 8: Bipartite Matching via the Hungarian Algorithm (<code>circuit.associate</code>)</h3>
        <p>Associating free-floating text labels with nearby component symbols is modeled as a <b>Minimum-Weight Bipartite Matching Problem</b>. A global cost matrix is computed based on Euclidean distance, orientation alignment, and prefix compatibility ($R \rightarrow \text{Resistor}$, $C \rightarrow \text{Capacitor}$):</p>
        <div class="formula-box">Cost = Euclidean_Distance + Prefix_Mismatch_Penalty + Orientation_Penalty</div>
        <p>Solved using the Kuhn-Munkres (Hungarian) algorithm (<code>scipy.optimize.linear_sum_assignment</code>), ensuring each component receives its mathematically optimal RefDes and value without duplicates.</p>
    </div>

    <div class="stage-card">
        <h3>Stage 9: Electrical Rules Check (ERC) & Confidence Scoring (<code>circuit.validate</code>)</h3>
        <p>Before compilation, the intermediate representation (<code>design.json</code>) undergoes automated Electrical Rules Checking:</p>
        <ul>
            <li>Checks for dangling single-pin nets, unconnected component pins, and duplicate RefDes.</li>
            <li>Flags floating active inputs, missing passive values, and polarized pin conflicts.</li>
        </ul>
        <p><b>Deterministic Confidence Formula:</b> Confidence is mathematically derived rather than guessed by an LLM:</p>
        <div class="formula-box">
            Confidence = 0.35 &times; C_symbols + 0.25 &times; C_ocr + 0.25 &times; (Connected_Pins / Total_Pins) + 0.15 &times; (Valid_Nets / Total_Nets) - &Sigma; ERC_Penalties
        </div>
    </div>
    """

    # -------------------------------------------------------------------------
    # PAGE 4: Cadence Compiler, Roundtrip Proof & Web Platform
    # -------------------------------------------------------------------------
    page4_html = """
    <h2>3. Deep Dive (Cont.): Cadence Compiler & Verification</h2>

    <div class="stage-card">
        <h3>Stage 10: Cadence OrCAD Capture Tcl Generation (<code>orcad.tcl_gen</code>)</h3>
        <p>Schematic2DSN translates the intermediate representation into clean, journal-verified Cadence Capture Tcl scripts:</p>
        <ul>
            <li><b>Grid Snapping:</b> Image coordinates ($Y$-down) are converted to OrCAD mils ($Y$-up) and snapped to Cadence's strict <b>100-mil electrical snap grid</b>.</li>
            <li><b>Mode A (Stub + Net Alias &mdash; Robust):</b> Places components, draws short orthogonal stubs from each pin, and attaches net aliases. OrCAD Capture natively bonds same-named aliases on the sheet. Highly robust and 100% editable.</li>
            <li><b>Mode B (Routed Polylines &mdash; Geometric):</b> Renders full orthogonal routed wire polylines matching original schematic visual paths.</li>
        </ul>
    </div>

    <div class="stage-card">
        <h3>Stage 11: Canonical Netlist Round-Trip Proof (<code>orcad.roundtrip</code>)</h3>
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

    <h2>4. Web Platform & Headless Cloud Deployment Architecture</h2>
    <p>Schematic2DSN provides an engineer-friendly Streamlit web interface with real-time feedback:</p>
    <ul>
        <li><b>Multi-Layer Vision Overlay:</b> Toggle between Raw Image, Text OCR, Wire Skeletons, Detected Symbols, and Solder Junctions.</li>
        <li><b>Live IR Inspector & Tcl Downloader:</b> Immediate JSON tree inspector, ERC warning logs, and one-click <code>design.tcl</code> download.</li>
        <li><b>Cloud Resilience:</b> Fully configured with <code>packages.txt</code> (providing <code>libgl1</code> and <code>libglib2.0-0</code>) to ensure headless Linux execution on Streamlit Community Cloud and Docker containers without graphics library failures.</li>
    </ul>

    <h2>5. How to Explain This Project in 60 Seconds (Elevator Pitch)</h2>
    <div class="highlight-card">
        <i>"Schematic2DSN solves the decades-old problem of legacy schematic lock-in. Instead of treating schematics as simple pictures, it acts like a compiler: it extracts lines, text, and electronic symbols, runs graph algorithms to discover the real circuit netlist, checks it for electrical errors, and outputs a native Cadence OrCAD Capture script. When an engineer opens the result in OrCAD, it's not a dumb image—it is a fully editable, 100-mil grid-snapped schematic where you can move resistors, edit values, simulate the netlist, and manufacture the board."</i>
    </div>
    """

    # -------------------------------------------------------------------------
    # PAGE 5: Benchmark Circuits Suite & Verification Metrics
    # -------------------------------------------------------------------------
    page5_html = """
    <h2>6. Benchmark Circuits Suite (12 Reference Circuits)</h2>
    <p>The repository contains 12 verified reference circuits with ground-truth netlists, available in <code>sample_schematics/</code>:</p>

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

    <h2>7. Quality Assurance & Test Verification Commands</h2>
    <div class="stage-card">
        <h3>1. Run the Entire Test Suite</h3>
        <p><code>pytest -v</code> &mdash; Executes all 163 unit and integration tests across all compiler stages in &lt;7 seconds.</p>
        <h3>2. Run CLI Pipeline on Any Benchmark PDF</h3>
        <p><code>python -m core.pipeline sample_schematics/voltage_divider.pdf out/</code></p>
        <h3>3. Launch Web Platform</h3>
        <p><code>streamlit run app/streamlit_app.py</code> &mdash; Open http://localhost:8501 and upload any schematic PDF from <code>sample_schematics/</code>.</p>
    </div>

    <div class="highlight-card" style="margin-top: 10px; text-align: center;">
        <b>Schematic2DSN &bull; Developed by Jatin Makhija (@JatinMakhija-10)</b><br>
        Email: jatinmakhija2007@gmail.com &bull; GitHub: https://github.com/JatinMakhija-10/Schematic2DSN
    </div>
    """

    pages = [page1_html, page2_html, page3_html, page4_html, page5_html]
    for i, content in enumerate(pages):
        page = doc.new_page(width=595, height=842) # A4
        rect = pymupdf.Rect(38, 38, 595 - 38, 842 - 38)
        page.insert_htmlbox(rect, content, css=css)
        
        # Footer
        footer_text = f"Schematic2DSN: Complete Technology & Solution Guide &bull; Author: Jatin Makhija &bull; Page {i+1} of {len(pages)}"
        page.insert_text(pymupdf.Point(595/2 - 150, 842 - 18), footer_text, fontsize=7.2, color=(0.4, 0.45, 0.5))

    primary_pdf = "Schematic2DSN_Complete_Explanation.pdf"
    doc.save(primary_pdf)
    doc.close()
    print(f"Generated primary PDF: {primary_pdf}")

    # Copy to user's Desktop for instant access
    desktop_copy = Path("C:/Users/JATIN/Desktop") / primary_pdf
    shutil.copyfile(primary_pdf, desktop_copy)
    print(f"Copied PDF directly to Desktop: {desktop_copy}")

if __name__ == "__main__":
    generate_pdf()
