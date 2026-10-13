# Schematic2DSN: Build Plan and Architecture

Prepared 8 Oct 2026. Demo 14 Oct. Team of 3. Target: schematic PDF or image in, editable OrCAD Capture design out.

## 1. Positioning and success definition

One sentence: we do not draw a picture of the schematic, we reconstruct the circuit graph and compile it into a native, editable OrCAD design.

Success means all of these work on the demo machine, live:

- Upload PDF, get overlay, IR JSON and a confidence report.
- Generate .DSN, open in Capture, move R1 and the wires follow.
- Change R1 from 10k to 15k and save.
- Run Capture's netlist export and it matches the IR automatically (round-trip check).
- Upload a bad schematic (diagonal wires, low resolution) and get a clear rejection reason.

Everything else is optional.

## 2. The hard truths that decide the project

1. The OrCAD write path is the critical path, not the AI. Prove it on Day 0 before any vision work.
2. The IR (intermediate representation) is the contract. If the IR is right, the DSN is right. Every stage reads and writes JSON files so each can be tested alone.
3. Connectivity is built from pin numbers, never pin labels. U1 pin 3 is physical pin 3, not the character "+".
4. A wire crossing without a dot is not a connection. A T-junction without a dot is a connection. A plus-shaped meeting needs a dot.
5. If the PDF is vector, read the vector data (PyMuPDF `page.get_drawings()` and `page.get_text("dict")`). That gives exact line segments and text with coordinates and removes most of the raster pipeline. Raster is the fallback, not the default.
6. Never let an LLM write the netlist or the DSN. An LLM may only classify a cropped symbol, clean an OCR string, or review the finished IR for suspicious items. Deterministic code owns connectivity.
7. Constrain the input and reject the rest. Rejection with a reason is a feature.

## 3. Architecture

```
input.pdf/png
   |
[S1 ingest]      -> page.png, page.meta.json (vector or raster, dpi, size)
   |
[S2 text]        -> texts.json  (string, bbox, rotation, confidence)
[S3 symbols]     -> symbols.json (class, bbox, rotation, mirror, confidence)
[S4 wires]       -> wires.json  (orthogonal segments, endpoints)
[S5 junctions]   -> junctions.json (dots)
   |
[S6 pins]        -> pins.json (component pin -> attachment point)
[S7 graph]       -> nets via union-find, labels, names
[S8 associate]   -> refdes and value assignment (Hungarian matching)
[S9 validate]    -> design.json (IR) + report.json
   |
[S10 export]     -> out.tcl -> Capture -> out.dsn
[S11 roundtrip]  -> netlist dumped from Capture, compared with IR
```

Rules for every stage:

- Pure function: file in, file out, no hidden state, fixed random seeds.
- A CLI entry point: `python -m vision.wires in/page.png out/wires.json`.
- A debug overlay PNG written to `out/debug/<stage>.png` showing what the stage believes. This is the fastest way to find bugs while vibe coding.
- Pydantic models for every JSON file. Schema version field in each file. Changing a schema means bumping the version and updating tests.

## 4. Repository layout

```
schematic2dsn/
  CLAUDE.md                  (rules for the coding assistant, see section 10)
  app/            streamlit_app.py, report_view.py
  core/           models.py (pydantic), config.py, geometry.py, units.py
  vision/         ingest.py, vector_extract.py, ocr.py, symbols_cv.py,
                  symbols_yolo.py, wires.py, junctions.py, pins.py
  circuit/        graph.py, associate.py, naming.py, validate.py, confidence.py
  orcad/          symbol_map.json, symbols.json, tcl_gen.py, launcher.py,
                  templates/*.tcl, library/COMPETITION.olb, roundtrip.py
  data/
    ref/          hand-built reference .dsn, journals, XML dumps
    synthetic/    generated test schematics + ground-truth netlists
    golden/       frozen inputs and expected IR
  tests/          per-stage tests, golden test
  out/            run outputs and debug overlays
```

Stack: Python 3.11, PyMuPDF, OpenCV, scikit-image (skeletonize), NumPy, SciPy (Hungarian), PaddleOCR, Ultralytics YOLOv8n, Pydantic, Streamlit, pytest. Optional: NetworkX for debugging graphs, a Claude vision call for ambiguous symbol crops.

## 5. Data contracts

### 5.1 IR (design.json), frozen on Day 0

```json
{
  "schema": "1.0",
  "design": {"name": "converted", "page": 1, "units": "mils", "grid": 100},
  "components": [
    {
      "id": "R1", "symbol_class": "RESISTOR", "value": "10k",
      "unit": 1, "position": {"x": 4200, "y": 2800},
      "rotation": 0, "mirror": false,
      "src_bbox_px": [x0, y0, x1, y1], "confidence": 0.96,
      "pins": [
        {"number": "1", "function": "A", "pos": {"x": 4000, "y": 2800}, "net": "VCC"},
        {"number": "2", "function": "B", "pos": {"x": 4400, "y": 2800}, "net": "NET_002"}
      ]
    }
  ],
  "nets": [
    {"name": "VCC", "auto_named": false,
     "pins": [["R1","1"]],
     "labels": [{"text": "VCC", "pos": {"x": 4200, "y": 3200}}]}
  ],
  "warnings": [{"code": "DANGLING_NET", "net": "NET_007", "detail": "one pin"}],
  "metadata": {"source": "schematic.pdf", "mode": "vector", "confidence": 0.94, "ocr_confidence": 0.97}
}
```

### 5.2 Three schema rules that prevent silent failures

1. Pin numbers are connectivity. Pin names are for display only.
2. Multi-unit parts carry `unit` (A, B, C). Same refdes, separate placements.
3. Power and ground symbols are net labels attached to a net, not two-pin components. The exporter chooses the Capture power symbol.

### 5.3 Other files

- `texts.json`: `{text, bbox, angle, conf}`.
- `symbols.json`: `{id, class, bbox, rotation, mirror, conf, source: cv|yolo|llm}`.
- `wires.json`: `{id, p0, p1}` axis-aligned segments in pixels, plus `endpoints` list.
- `junctions.json`: `{pos, radius}`.
- `orcad/symbols.json` (the library contract): per symbol class, library name, symbol name, nominal body length in mils, and for each rotation 0/90/180/270 and mirror state the pin number, function name and the pin end offset from the part origin in mils. Pin functions let the vision side say "base" or "anode" without knowing library pin numbers.

## 6. Stage specifications

### S1 Ingest

- Detect vector vs raster: a PDF page with more than N drawing paths and real text is vector.
- Raster path: render at 600 DPI for line work. Grayscale, Otsu or adaptive threshold, remove specks under 6 px area, deskew using the dominant Hough angle (reject if skew over 2 degrees after correction fails).
- Reject rules (return a machine-readable code and a human sentence): multi-page, under 200 DPI equivalent, more than 5 percent of line segments off-axis by over 3 degrees, image under 1200 px on the long side, color-heavy photo.
- Store `pixel_per_mil_hint` if the sheet size is known from the PDF page size.

### S2 Text

- Vector: pull spans from `get_text("dict")`, keep angle from the line direction. No OCR needed.
- Raster: PaddleOCR, run at 0 and 90 degrees because vertical components carry rotated labels. Merge results, keep the higher confidence per overlapping box.
- Post-process with regexes tied to context, not blind replacement:
  - Refdes: `^[A-Z]{1,3}[0-9]{1,3}[A-Z]?$`. Fix O to 0, l or I to 1 only when the shape of the string matches this pattern.
  - Values: normalize `u`, `µ`, `μ` to `u`; `Ω` and `R` and `ohm` to ohm; `4k7` to 4.7k; `.1uF` to 0.1uF; `10K` to 10k. Keep the raw string too.
  - Class prefix check: a RESISTOR must be R\*, capacitor C\*, inductor L\*, diode D\*, LED D\* or LED\*, transistor Q\*, IC U\*, connector J\* or P\*.
- Domain dictionary: VCC, VDD, GND, VIN, VOUT, VREF, SDA, SCL, RESET, +5V, +3V3, 3V3, -12V, LM, NE, MC, IRF, 2N, BC.

### S3 Symbols

- Mask text boxes first so letters do not become shapes.
- Level 1, OpenCV, no training: contour and shape heuristics for resistor (zig-zag with 6 or more turns, or a thin rectangle for IEC style), capacitor (two parallel plates with a gap), inductor (arcs or coils), diode and LED (triangle plus bar, LED adds two arrows), ground (stacked decreasing lines or the three-line earth), VCC (arrow or bar on a stub), op-amp (triangle with two inputs on one side).
- Level 2, YOLOv8n on synthetic data: 12 classes (resistor, capacitor, inductor, diode, led, ground, vcc, opamp, npn, pnp, nmos, pmos, connector). Generate 500 to 1000 images by exporting KiCad symbol SVGs, rotating by 0/90/180/270, mirroring, adding wires as stubs, noise, blur, JPEG artifacts. Auto-annotate from the placement. 50 to 100 epochs.
- Both levels run; if they disagree, prefer the higher confidence, and send crops under 0.8 confidence to the optional LLM classifier with a closed label set.
- Rotation and mirror: for polarized or oriented symbols, derive from the geometry (diode triangle direction, transistor base bar side, emitter arrow, op-amp input side).
- Style flag: record ANSI (zig-zag) vs IEC (rectangle) per document and reuse across symbols.

### S4 Wires

- Vector path: take horizontal and vertical line segments from `get_drawings()`. Discard segments inside component bboxes. Merge collinear touching segments. Done.
- Raster path:
  1. Remove component and text regions (dilate bboxes by 3 px) from the line mask. Without this, a resistor zig-zag turns into wires.
  2. Skeletonize.
  3. Probabilistic Hough with min length about 0.6 times median line thickness times 8, then snap angles to 0 or 90.
  4. Merge collinear segments within 2 px lateral and 3 px gap.
  5. Split segments at T intersections.
- Output segments with integer pixel endpoints.

### S5 Junctions

- Dots are found by morphological opening with a disc larger than the line thickness. Opening erases lines and leaves filled dots. Take connected components with circularity above 0.7.
- Do this before skeletonization because a dot distorts the skeleton.
- Rule set stored in `core/config.py`:
  - T meeting: connected.
  - Corner meeting: connected.
  - Plus (four-way) crossing: connected only if a dot exists at the crossing.
  - Anything ambiguous goes to `warnings` as AMBIGUOUS\_JUNCTION and is treated as not connected unless a flag says otherwise.

### S6 Pins

- Component pin positions come from the library contract, not from the image alone: take the detected body bbox, rotation and mirror, then compute expected pin ends from `orcad/symbols.json` scaled to pixels.
- Snap each expected pin end to the nearest wire endpoint within tolerance (default 6 px at 600 DPI, tune per document using median line thickness).
- If no endpoint is in tolerance, flag UNCONNECTED\_PIN rather than inventing a connection.
- Passives are electrically symmetric. Assign pin 1 to the left or top end deterministically so output is stable. Polarized parts map by function (anode, cathode, base, collector, emitter, gate, drain, source).

### S7 Graph

- Nodes: wire endpoints, junction points, pin attachment points, label attachment points.
- Edges: each segment, plus implicit edges where endpoints are within tolerance, plus split points on T meetings.
- Union-find. Each set is a net.
- Labels attach to the nearest segment within tolerance. Same text on two sets merges them (global label convention). A ground symbol attaches to its stub wire and names the net GND. Multiple ground types all map to GND with a GROUND\_VARIANT warning.
- Net names: label text if present, else `NET_001`, `NET_002` in a stable order (sorted by min pin id) so diffs are readable.

### S8 Associate

- Build a cost matrix between components and candidate refdes texts, and another for values. Cost is distance plus penalties for wrong side (text sitting on a wire), wrong prefix, wrong value type.
- Solve with `scipy.optimize.linear_sum_assignment` so one text is never used twice.
- Unmatched components get auto refdes (`R?` style placeholder is not allowed in Capture output; use `R_AUTO1`) and a warning.

### S9 Validate

Table of checks, each emitting a coded warning or error: unconnected pin, single-pin net, duplicate refdes, symbol with no library mapping (reject with reason), refdes prefix mismatch, net with two different labels (conflict), pin on two different nets (impossible; indicates a snapping bug), component with no pins found.

Confidence is a documented formula, not a made-up number: weighted mean of symbol conf, OCR conf, fraction of pins connected, fraction of nets with 2 or more pins, minus penalties per warning. Show the formula in the UI.

## 7. OrCAD details that bite

### 7.1 Known from public documentation

- Reading is well supported through the Dbo classes. Writing is thinner. `PlacePart(x, y, libName, pkgName, device, bool)` and `SelectObject(x, y, bool)` are documented user actions.
- Journaling: `SetOptionBool Journaling TRUE` and `SetOptionBool DisplayCommands TRUE` in the Capture command window, or Options > Extended Preferences. Every GUI action becomes a replayable Tcl command.
- `XMATIC_DSN2XML <dsn> <xml>` dumps the internal database to XML. `XMATIC_XML2DSN` goes back. Keep XML2DSN as fallback.

### 7.2 Strategy: journal first

Build tiny designs by hand with journaling on, copy the logged commands, replace constants with variables, replay. Reference set to build on Day 0 hour 0 to 3:

| File | Content | Learns |
| --- | --- | --- |
| ref\_R.dsn | R1, 2 wires, GND, VCC | place part, wire, power symbol |
| ref\_RC.dsn | R1, C1, one junction | junction representation |
| ref\_label.dsn | two wires with the same net alias | connect by name |
| ref\_opamp.dsn | 5-pin op-amp symbol, 3 wires | multi-pin placement |
| ref\_rot.dsn | R rotated 90, mirrored | rotation and mirror commands |

Run DSN2XML on each and commit the XML.

### 7.3 Two export modes (build both, default to A)

- Mode A, stub and alias (robust): place every part, then for each pin draw a short orthogonal wire stub off the pin end and attach a net alias with the net name. Capture connects same-named nets on a page. No routing needed, electrically exact, still fully editable. Looks busier.
- Mode B, routed (pretty): from the IR, draw orthogonal polylines between pin ends using the original wire segments scaled to mils. Use only if Mode A is stable and time remains.

Demo with Mode B on the simplest circuits, Mode A for the rest, and say so honestly if asked.

### 7.4 Small details

- Grid: Capture's schematic grid is 100 mils by default and pin ends sit on it. Snap every placement to 100 mils (verify your install). An off-grid wire end looks connected and is not.
- Wire end must land exactly on the pin end point, not on the symbol body.
- Coordinates: image y is down, Capture y is up. Transform once in `core/geometry.py`, nowhere else.
- Scale: do not fit to sheet by width alone. Compute scale so the median passive body length in pixels equals the library symbol's nominal length in mils, then check the drawing fits the sheet; if not, pick a larger sheet size (C, D) and say so in the report.
- Library symbols must match the source drawing's pin layout. If the source op-amp shows V+ and V-, use a 5-pin symbol with visible power pins, not the LM358 split-package symbol with hidden power pins.
- Multi-unit packages: place each unit separately with the same refdes and `unit` index. For the demo, prefer single-unit symbols unless time is plentiful.
- Refdes and value: placing a part usually auto-assigns `R?`. Set properties right after placement using the journaled property command. Turn off auto-increment effects so numbers do not shift.
- Power symbols carry the net name through their text; confirm the exact property that holds it in the journal.
- Case: Capture net names are case-insensitive in many contexts; normalize to upper case in the IR.
- Project vs design: a lone .dsn can open, but create a proper project (.opj) so the netlist menu works.
- Run mechanism: Python writes `out.tcl`. `launcher.py` opens Capture and sources the script from the command window (`source C:/path/out.tcl`). If there is no command-line hook, drive the window with pywinauto or AutoHotkey. Decide on Day 0.
- Licensing and edition: check part and pin limits of your Capture edition and that the demo machine has the license. Record a backup video of the full flow on Day 5.

### 7.5 Round-trip verification

After generation, dump the netlist from Capture (read-only Tcl iterating parts, pins, nets, or the Create Netlist command) and compare with the IR using a canonical form: set of sets of (refdes, pin), ignoring net names. Mismatch fails the run. This turns the demo's netlist step into an automatic proof.

## 8. Testing strategy

- Ground truth for free: KiCad can export a schematic to PDF and a netlist from the same file (`kicad-cli`). Build 20 circuits of rising difficulty: divider, RC filter, LED driver, inverting op-amp, common emitter, H-bridge, 555 astable. Each gives an input PDF and a true netlist.
- Metrics: component recall and precision, refdes accuracy, value accuracy, and net partition match (exact match rate plus per-net F1). Netlist equality is the headline number.
- Golden test (freeze Day 5): 5 schematics, expected IR checked in, pytest fails on any diff in the canonical netlist.
- Per-stage tests: wire merge, T vs plus junction, rotated text, value normalization table, coordinate transform round trip, pin snapping tolerance.
- Fuzz the IR exporter: random valid IRs (3 to 15 parts) through Capture to see if the Tcl layer holds.

## 9. Schedule (8 to 14 Oct)

**Day 0, 8 Oct: OrCAD hello world (all three, P3 leads)**

- Confirm Capture version, license, how Tcl is run, journaling works.
- Hand-build the 5 reference designs with journaling, dump XML.
- Build COMPETITION.olb: R, C, L, D, LED, GND, VCC, 5-pin op-amp, NPN, PNP, NMOS, PMOS, connector header.
- Hard-coded `tcl_gen.py` for R1, C1, GND, VCC. Open result, move R1, edit value.
- Gate: by end of day, either Mode A works or XML2DSN works. If both fail, shrink to netlist-only export and tell the team on Day 1 morning.
- P1 and P2 in parallel: set up repo, models.py, freeze the IR, write the KiCad test generator.

**Day 1, 9 Oct: vision v0**

- Ingest, vector extraction, OCR, OpenCV symbol detection for R, C, GND, VCC, wires and junctions. Debug overlays for each. Output the three JSON files for 3 circuits.
- P3: Tcl generator from a hand-written IR with 3 parts, then 8 parts.

**Day 2, 10 Oct: graph and IR**

- Pin snapping, union-find, labels, association, validation. Output design.json for all 3 circuits. Netlist comparison against KiCad truth.
- P3: Mode A on arbitrary IR, rotation and mirror, library mapping.

**Day 3, 11 Oct: end-to-end**

- design.json to DSN with no manual step. Round-trip verification. Reject path.
- Start YOLO training in background on synthetic data if CV heuristics miss over 15 percent.

**Day 4, 12 Oct: breadth (registration deadline day, confirm the entry is submitted)**

- 10 test circuits, log every failure into a table with a category. Fix by frequency. Add transistors, op-amp, diode orientation, rotation.

**Day 5, 13 Oct: freeze and polish**

- Freeze golden test. Streamlit UI with overlay, report, IR viewer, Generate button. Record a backup video. Rehearse twice with a timer. No new features.

**Day 6, 14 Oct: demo**

## 10. Vibe coding protocol

### 10.1 Rules file for the coding assistant (save as CLAUDE.md)

```
Project: Schematic2DSN. Image or PDF schematic to editable OrCAD Capture design.
Read docs/PLAN.md and core/models.py before editing anything.

Rules:
1. Connectivity uses pin numbers only. Never pin labels.
2. Every stage is a pure function with a CLI and a debug overlay PNG.
3. All JSON passes through pydantic models in core/models.py. Do not change a
   model without bumping the schema version and updating tests.
4. Coordinate conversion lives only in core/geometry.py.
5. Tolerances and thresholds live only in core/config.py. No magic numbers.
6. No LLM may produce connectivity or Tcl. Deterministic code only.
7. Write the test first for any bug fix. Run pytest before saying done.
8. Small diffs. One module per task. Do not refactor files you were not asked to.
9. Never invent Capture Tcl commands. Use only commands found in data/ref journals
   or the docs. If a command is unknown, say so and ask for a journal capture.
10. Output style: no placeholders, no TODOs left silently, fail loudly with codes.
```

Rule 9 matters most. A coding assistant will confidently invent plausible Tcl that does not exist in Capture.

### 10.2 Prompt template per task

```
Task: implement <module/function>.
Inputs: <file + pydantic model>. Outputs: <file + model>.
Spec: <paste the stage section from this plan>.
Test data: data/synthetic/<case>/.
Done when: <metric or test name> passes and the debug overlay shows <what>.
Do not touch: <files>.
```

### 10.3 Order of work in the repo

1. models.py and config.py.
2. geometry.py with tests (round trip px to mils and back).
3. The KiCad test generator.
4. orcad/tcl\_gen.py driven by hand-written IR (independent of vision).
5. vision stages one at a time, each against ground truth.
6. circuit stages.
7. roundtrip.py.
8. UI last.

### 10.4 Habits that save hours

- After every stage change, open the overlay before reading code.
- Keep a `failures.md` table: case, stage that failed, cause, fix. It is the roadmap for Day 4.
- Commit after every green test. Tag `golden-v1` on Day 5.
- Pin library versions in requirements.txt (PaddleOCR and Ultralytics change APIs).
- Cache OCR and YOLO outputs on disk by file hash to speed iteration.

## 11. Skills by role

| Role | Needs |
| --- | --- |
| P1 Vision | OpenCV morphology and Hough, skeletonization, PyMuPDF vector extraction, PaddleOCR tuning, YOLO training, synthetic data generation, debugging with overlays |
| P2 Circuit graph | Union-find, geometry tolerances, bipartite matching (Hungarian), pydantic schemas, pytest, metric design, KiCad netlist parsing |
| P3 OrCAD | Capture GUI fluency, symbol and library creation, Tcl, Dbo model basics, journaling, XML reading, Windows automation (pywinauto or AutoHotkey) |
| All | Git hygiene, reading overlays, writing a failure log, rehearsing a demo |

If P3 is not already fluent in Capture, P1 pairs with them on Day 0. This is the one place where idle hands are not allowed.

## 12. Risks and fallbacks

| Risk | Likelihood | Fallback |
| --- | --- | --- |
| Tcl cannot create wires | Medium | Mode A with net aliases, or XML2DSN |
| Both OrCAD paths fail | Low | Export netlist, show IR and overlay, be honest about the scope |
| Raster wires noisy | High | Require vector PDF for the live demo, raster as a stretch |
| OCR confuses 10k and 100k | High | Context regex, class prefix checks, flag low confidence values for manual edit in UI |
| YOLO under 80 percent | Medium | OpenCV rules only, narrower class list |
| Junction ambiguity | Medium | Require dots, reject or warn |
| Multi-unit op-amp fails | Medium | Single-unit 5-pin op-amp symbol |
| Capture license or machine issue | Low | Backup video, pre-generated .dsn, XML output |
| Scope creep | High | Section 13 list is the only demo scope |

## 13. Scope lock

In scope: single page, clean PDF or PNG, orthogonal wires, the 12 classes, refdes, values, net labels, power symbols, junction dots.

Out of scope: hierarchy, buses, multi-page, hand-drawn input, diagonal wires, custom symbols, footprints, PCB.

## 14. Demo script (5 minutes)

1. Show the source PDF on screen.
2. Upload, press Analyze.
3. Overlay appears with component and net counts and the confidence breakdown.
4. Show the IR JSON briefly: "the circuit as data".
5. Press Generate OrCAD.
6. Capture opens the design.
7. Move R1, wires follow. Change 10k to 15k.
8. Run the netlist check: green match with the IR.
9. Upload a bad file, show the rejection reason.
10. Close with: we do not generate an image of the schematic, we reconstruct the circuit itself.

## 15. Day 0 questions to answer before writing vision code

- Which Capture version and edition, and what are the part limits?
- How does the Tcl script get executed headlessly, or does it need window automation?
- Exact commands for: create design, place part, rotate, mirror, set refdes and value, draw wire, place net alias, place power symbol, save.
- Which property holds the power symbol net name?
- Pin end offsets for each library symbol at every rotation and mirror.
- Does journaling capture wire drawing as a single command or a click sequence?
- Can the netlist be dumped by Tcl, or only through the menu?

Answers go into `data/ref/NOTES.md` and are the only source the assistant may use for OrCAD commands.
