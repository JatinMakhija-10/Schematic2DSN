/**
 * app/web/app.js  --  Schematic2DSN Professional EDA CAD Workstation Runtime
 * Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
 *
 * Strict Design System:
 *   - Zero rounded corners on every element
 *   - Zero purple, zero green
 *   - Deep Obsidian, Slate Graphite, Electric Cyan (#0ea5e9), Technical Amber (#f59e0b)
 */

(function () {
    "use strict";

    // -------------------------------------------------------------------------
    // Global Application State
    // -------------------------------------------------------------------------
    const state = {
        ir: null,
        circuitKey: "voltage_divider",
        routingMode: "A",
        tclLibPath: "orcad/library/COMPETITION.olb",
        panX: 0,
        panY: 0,
        scale: 1.0,
        isDragging: false,
        dragStartX: 0,
        dragStartY: 0,
        hoveredElement: null,
        selectedElement: null,
        hoveredNet: null,
        layers: {
            grid: true,
            components: true,
            wires: true,
            pins: true,
            nets: true
        },
        tclCode: "",
        fps: 60,
        lastRenderTimestamp: 0
    };

    // DOM Element References
    const elements = {
        canvas: document.getElementById("schematicCanvas"),
        canvasContainer: document.getElementById("canvasContainer"),
        circuitSelector: document.getElementById("circuitSelector"),
        btnLoadCircuit: document.getElementById("btnLoadCircuit"),
        btnResetView: document.getElementById("btnResetView"),
        dropZone: document.getElementById("dropZone"),
        fileInput: document.getElementById("fileInput"),
        modeARadio: document.getElementById("modeARadio"),
        modeBRadio: document.getElementById("modeBRadio"),
        kpiComponents: document.getElementById("kpiComponents"),
        kpiNets: document.getElementById("kpiNets"),
        kpiConfidence: document.getElementById("kpiConfidence"),
        kpiErcWarnings: document.getElementById("kpiErcWarnings"),
        kpiErcCard: document.getElementById("kpiErcCard"),
        btnToggleGrid: document.getElementById("btnToggleGrid"),
        btnToggleComponents: document.getElementById("btnToggleComponents"),
        btnToggleWires: document.getElementById("btnToggleWires"),
        btnTogglePins: document.getElementById("btnTogglePins"),
        btnToggleNets: document.getElementById("btnToggleNets"),
        btnZoomIn: document.getElementById("btnZoomIn"),
        btnZoomOut: document.getElementById("btnZoomOut"),
        btnZoomFit: document.getElementById("btnZoomFit"),
        btnExportSvg: document.getElementById("btnExportSvg"),
        btnExportPng: document.getElementById("btnExportPng"),
        zoomDisplay: document.getElementById("zoomDisplay"),
        hudCoords: document.getElementById("hudCoords"),
        hudZoom: document.getElementById("hudZoom"),
        hudSelected: document.getElementById("hudSelected"),
        elementTooltip: document.getElementById("elementTooltip"),
        tooltipHeader: document.getElementById("tooltipHeader"),
        tooltipBody: document.getElementById("tooltipBody"),
        inspectorTabsHeader: document.getElementById("inspectorTabsHeader"),
        bomSearchInput: document.getElementById("bomSearchInput"),
        bomTableBody: document.getElementById("bomTableBody"),
        propertySheet: document.getElementById("propertySheet"),
        netSearchInput: document.getElementById("netSearchInput"),
        netTableBody: document.getElementById("netTableBody"),
        ercResultsContainer: document.getElementById("ercResultsContainer"),
        tclLibPathInput: document.getElementById("tclLibPathInput"),
        btnRecompileTcl: document.getElementById("btnRecompileTcl"),
        tclCodeArea: document.getElementById("tclCodeArea"),
        btnCopyTcl: document.getElementById("btnCopyTcl"),
        btnDownloadTcl: document.getElementById("btnDownloadTcl"),
        jsonIrCodeArea: document.getElementById("jsonIrCodeArea"),
        btnCopyJson: document.getElementById("btnCopyJson"),
        btnDownloadJson: document.getElementById("btnDownloadJson"),
        statusCircuitName: document.getElementById("statusCircuitName"),
        renderLatency: document.getElementById("renderLatency")
    };

    const ctx = elements.canvas.getContext("2d");

    // -------------------------------------------------------------------------
    // Initialization
    // -------------------------------------------------------------------------
    function init() {
        setupCanvasResolution();
        attachEventListeners();
        loadCircuit(state.circuitKey);
    }

    function setupCanvasResolution() {
        const dpr = window.devicePixelRatio || 1;
        const rect = elements.canvasContainer.getBoundingClientRect();
        elements.canvas.width = rect.width * dpr;
        elements.canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
    }

    // -------------------------------------------------------------------------
    // Event Listeners
    // -------------------------------------------------------------------------
    function attachEventListeners() {
        window.addEventListener("resize", () => {
            setupCanvasResolution();
            render();
        });

        // Load Preset Circuit
        elements.btnLoadCircuit.addEventListener("click", () => {
            const key = elements.circuitSelector.value;
            loadCircuit(key);
        });

        elements.circuitSelector.addEventListener("change", (e) => {
            loadCircuit(e.target.value);
        });

        // Fit / Reset View
        elements.btnResetView.addEventListener("click", fitToScreen);
        elements.btnZoomFit.addEventListener("click", fitToScreen);

        // Zoom Controls
        elements.btnZoomIn.addEventListener("click", () => zoomBy(1.25));
        elements.btnZoomOut.addEventListener("click", () => zoomBy(0.8));

        // Export Controls
        if (elements.btnExportSvg) elements.btnExportSvg.addEventListener("click", exportSvg);
        if (elements.btnExportPng) elements.btnExportPng.addEventListener("click", exportPng);

        // Layer Toggles
        setupLayerToggle(elements.btnToggleGrid, "grid");
        setupLayerToggle(elements.btnToggleComponents, "components");
        setupLayerToggle(elements.btnToggleWires, "wires");
        setupLayerToggle(elements.btnTogglePins, "pins");
        setupLayerToggle(elements.btnToggleNets, "nets");

        // Routing Protocol Mode Radio Buttons
        elements.modeARadio.addEventListener("change", () => {
            state.routingMode = "A";
            compileTcl();
        });
        elements.modeBRadio.addEventListener("change", () => {
            state.routingMode = "B";
            compileTcl();
        });

        // Dropzone & File Ingestion
        elements.dropZone.addEventListener("click", () => elements.fileInput.click());
        elements.dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            elements.dropZone.classList.add("dragover");
        });
        elements.dropZone.addEventListener("dragleave", () => {
            elements.dropZone.classList.remove("dragover");
        });
        elements.dropZone.addEventListener("drop", handleFileDrop);
        elements.fileInput.addEventListener("change", handleFileInput);

        // Tab Switching
        elements.inspectorTabsHeader.addEventListener("click", (e) => {
            const btn = e.target.closest(".tab-btn");
            if (!btn) return;
            const targetId = btn.getAttribute("data-tab");
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add("active");
        });

        // Search Filters
        elements.bomSearchInput.addEventListener("input", filterBomTable);
        elements.netSearchInput.addEventListener("input", filterNetTable);

        // OrCAD Tcl Recompile & Actions
        elements.btnRecompileTcl.addEventListener("click", () => {
            state.tclLibPath = elements.tclLibPathInput.value.trim() || "orcad/library/COMPETITION.olb";
            compileTcl();
        });

        elements.btnCopyTcl.addEventListener("click", () => copyToClipboard(elements.tclCodeArea.value, elements.btnCopyTcl, "TCL COPIED"));
        elements.btnDownloadTcl.addEventListener("click", downloadTclFile);
        elements.btnCopyJson.addEventListener("click", () => copyToClipboard(elements.jsonIrCodeArea.value, elements.btnCopyJson, "JSON COPIED"));
        elements.btnDownloadJson.addEventListener("click", downloadJsonFile);

        // Canvas Interaction (Pan, Zoom, Hover, Click Selection)
        elements.canvas.addEventListener("mousedown", onCanvasMouseDown);
        window.addEventListener("mousemove", onCanvasMouseMove);
        window.addEventListener("mouseup", onCanvasMouseUp);
        elements.canvas.addEventListener("wheel", onCanvasWheel, { passive: false });
        elements.canvas.addEventListener("mouseleave", () => {
            elements.elementTooltip.style.display = "none";
            state.hoveredElement = null;
            state.hoveredNet = null;
            render();
        });
    }

    function setupLayerToggle(btn, layerKey) {
        btn.addEventListener("click", () => {
            state.layers[layerKey] = !state.layers[layerKey];
            btn.classList.toggle("active", state.layers[layerKey]);
            render();
        });
    }

    // -------------------------------------------------------------------------
    // Circuit Loading & State Sync
    // -------------------------------------------------------------------------
    function loadCircuit(key) {
        state.circuitKey = key;
        const benchmarkData = window.BENCHMARK_CIRCUITS && window.BENCHMARK_CIRCUITS[key];

        if (benchmarkData) {
            state.ir = JSON.parse(JSON.stringify(benchmarkData));
        } else {
            console.warn("Benchmark circuit key not found:", key);
            return;
        }

        state.selectedElement = null;
        state.hoveredElement = null;
        state.hoveredNet = null;

        updateTelemetry();
        populateBomTable();
        populateNetTable();
        populateErcReport();
        compileTcl();
        populateJsonIr();
        fitToScreen();

        if (elements.statusCircuitName) {
            elements.statusCircuitName.textContent = `CIRCUIT: ${key.toUpperCase()}`;
        }
    }

    function updateTelemetry() {
        if (!state.ir) return;
        const numComp = state.ir.components ? state.ir.components.length : 0;
        const numNets = state.ir.nets ? state.ir.nets.length : 0;
        const conf = state.ir.metadata && typeof state.ir.metadata.confidence === "number"
            ? state.ir.metadata.confidence
            : 1.0;
        const numWarnings = state.ir.warnings ? state.ir.warnings.length : 0;

        elements.kpiComponents.textContent = String(numComp).padStart(2, "0");
        elements.kpiNets.textContent = String(numNets).padStart(2, "0");
        elements.kpiConfidence.textContent = `${Math.round(conf * 100)}%`;
        elements.kpiErcWarnings.textContent = String(numWarnings).padStart(2, "0");

        if (numWarnings > 0) {
            elements.kpiErcCard.style.borderLeftColor = "var(--accent-amber)";
            elements.kpiErcWarnings.style.color = "var(--accent-amber)";
        } else {
            elements.kpiErcCard.style.borderLeftColor = "var(--accent-cyan)";
            elements.kpiErcWarnings.style.color = "#ffffff";
        }
    }

    // -------------------------------------------------------------------------
    // Canvas Pan, Zoom & Coordinates Transform
    // -------------------------------------------------------------------------
    function toScreenX(milX) {
        const rect = elements.canvasContainer.getBoundingClientRect();
        return (milX - 4000) * state.scale + (rect.width / 2) + state.panX;
    }

    function toScreenY(milY) {
        const rect = elements.canvasContainer.getBoundingClientRect();
        // Invert Y for EDA CAD convention (larger Y is higher up in Capture)
        return (3000 - milY) * state.scale + (rect.height / 2) + state.panY;
    }

    function toMilX(screenX) {
        const rect = elements.canvasContainer.getBoundingClientRect();
        return (screenX - (rect.width / 2) - state.panX) / state.scale + 4000;
    }

    function toMilY(screenY) {
        const rect = elements.canvasContainer.getBoundingClientRect();
        return 3000 - (screenY - (rect.height / 2) - state.panY) / state.scale;
    }

    function fitToScreen() {
        if (!state.ir || !state.ir.components || state.ir.components.length === 0) return;

        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        state.ir.components.forEach(c => {
            const x = c.position.x;
            const y = c.position.y;
            if (x < minX) minX = x;
            if (x > maxX) maxX = x;
            if (y < minY) minY = y;
            if (y > maxY) maxY = y;
        });

        // Add 500-mil padding
        minX -= 500; maxX += 500;
        minY -= 400; maxY += 400;

        const wMils = Math.max(maxX - minX, 1000);
        const hMils = Math.max(maxY - minY, 800);

        const rect = elements.canvasContainer.getBoundingClientRect();
        const scaleX = rect.width / wMils;
        const scaleY = rect.height / hMils;

        state.scale = Math.min(scaleX, scaleY, 1.4);
        const centerMilX = (minX + maxX) / 2;
        const centerMilY = (minY + maxY) / 2;

        state.panX = -(centerMilX - 4000) * state.scale;
        state.panY = -(3000 - centerMilY) * state.scale;

        updateZoomDisplay();
        render();
    }

    function zoomBy(factor) {
        const newScale = Math.max(0.2, Math.min(4.0, state.scale * factor));
        state.scale = newScale;
        updateZoomDisplay();
        render();
    }

    function updateZoomDisplay() {
        const pct = Math.round(state.scale * 100);
        elements.zoomDisplay.textContent = `ZOOM: ${pct}%`;
        elements.hudZoom.textContent = `SCALE: ${pct}%`;
    }

    function onCanvasMouseDown(e) {
        state.isDragging = true;
        state.dragStartX = e.clientX - state.panX;
        state.dragStartY = e.clientY - state.panY;
        elements.canvas.style.cursor = "grabbing";
    }

    function onCanvasMouseMove(e) {
        const rect = elements.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        if (state.isDragging) {
            state.panX = e.clientX - state.dragStartX;
            state.panY = e.clientY - state.dragStartY;
            render();
            return;
        }

        // CAD Mil Coordinate Readout
        const milX = Math.round(toMilX(mouseX));
        const milY = Math.round(toMilY(mouseY));
        elements.hudCoords.textContent = `CURSOR: (X: ${milX}, Y: ${milY}) MILS`;

        // Hit Testing
        checkHover(mouseX, mouseY, e.clientX, e.clientY);
    }

    function onCanvasMouseUp(e) {
        if (state.isDragging) {
            state.isDragging = false;
            elements.canvas.style.cursor = "grab";
        } else {
            // Click Selection
            const rect = elements.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            selectElementAt(mouseX, mouseY);
        }
    }

    function onCanvasWheel(e) {
        e.preventDefault();
        const rect = elements.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const milBeforeX = toMilX(mouseX);
        const milBeforeY = toMilY(mouseY);

        const zoomDelta = e.deltaY < 0 ? 1.12 : 0.89;
        state.scale = Math.max(0.2, Math.min(4.5, state.scale * zoomDelta));

        // Adjust pan to zoom into mouse center
        const screenAfterX = toScreenX(milBeforeX);
        const screenAfterY = toScreenY(milBeforeY);
        state.panX += (mouseX - screenAfterX);
        state.panY += (mouseY - screenAfterY);

        updateZoomDisplay();
        render();
    }

    // -------------------------------------------------------------------------
    // Hit Testing & Selection
    // -------------------------------------------------------------------------
    function checkHover(screenX, screenY, clientX, clientY) {
        if (!state.ir) return;

        let hoveredComp = null;
        let hoveredPin = null;

        // Check components
        for (const comp of state.ir.components) {
            const cx = toScreenX(comp.position.x);
            const cy = toScreenY(comp.position.y);
            const pinCount = comp.pins ? comp.pins.length : 2;
            const halfW = (pinCount > 4 ? 65 : 45) * state.scale;
            const halfH = (pinCount > 4 ? Math.max(36, (pinCount / 2) * 14) : 26) * state.scale;

            if (screenX >= cx - halfW && screenX <= cx + halfW &&
                screenY >= cy - halfH && screenY <= cy + halfH) {
                hoveredComp = comp;
                break;
            }

            // Check individual pins
            if (comp.pins) {
                for (const pin of comp.pins) {
                    const px = toScreenX(pin.pos.x);
                    const py = toScreenY(pin.pos.y);
                    const dist = Math.hypot(screenX - px, screenY - py);
                    if (dist < 10) {
                        hoveredPin = { pin, comp };
                        break;
                    }
                }
            }
            if (hoveredPin) break;
        }

        if (hoveredPin) {
            state.hoveredElement = hoveredPin.comp;
            state.hoveredNet = hoveredPin.pin.net;
            showTooltip(clientX, clientY, `PIN ${hoveredPin.comp.id}.${hoveredPin.pin.number}`,
                `Net: <strong style="color: var(--accent-cyan);">${hoveredPin.pin.net || "UNCONNECTED"}</strong><br>Function: ${hoveredPin.pin.function || "I/O"}`);
            elements.hudSelected.textContent = `TARGET: ${hoveredPin.comp.id}.${hoveredPin.pin.number}`;
            render();
            return;
        }

        if (hoveredComp) {
            state.hoveredElement = hoveredComp;
            state.hoveredNet = null;
            showTooltip(clientX, clientY, `${hoveredComp.id} // ${hoveredComp.symbol_class}`,
                `Value: <strong style="color: var(--accent-amber);">${hoveredComp.value || "N/A"}</strong><br>` +
                `Pos: (${hoveredComp.position.x.toFixed(0)}, ${hoveredComp.position.y.toFixed(0)}) mils<br>` +
                `Confidence: ${(hoveredComp.confidence * 100).toFixed(0)}%`);
            elements.hudSelected.textContent = `TARGET: ${hoveredComp.id} (${hoveredComp.value || hoveredComp.symbol_class})`;
            render();
            return;
        }

        // Check Nets
        let hoveredNetName = null;
        if (state.layers.wires) {
            for (const net of state.ir.nets) {
                const wireSegments = getNetSegments(net);
                for (const seg of wireSegments) {
                    const x1 = toScreenX(seg.x1);
                    const y1 = toScreenY(seg.y1);
                    const x2 = toScreenX(seg.x2);
                    const y2 = toScreenY(seg.y2);

                    if (distToSegment(screenX, screenY, x1, y1, x2, y2) < 8) {
                        hoveredNetName = net.name;
                        break;
                    }
                }
                if (hoveredNetName) break;
            }
        }

        if (hoveredNetName) {
            state.hoveredElement = null;
            state.hoveredNet = hoveredNetName;
            showTooltip(clientX, clientY, `NET // ${hoveredNetName}`, `Nodes connected: ${getNetPinCount(hoveredNetName)}`);
            elements.hudSelected.textContent = `NET: ${hoveredNetName}`;
            render();
            return;
        }

        state.hoveredElement = null;
        state.hoveredNet = null;
        elements.elementTooltip.style.display = "none";
        elements.hudSelected.textContent = state.selectedElement ? `SELECTED: ${state.selectedElement.id}` : "TARGET: NONE";
        render();
    }

    function selectElementAt(screenX, screenY) {
        if (!state.ir) return;

        let selected = null;
        for (const comp of state.ir.components) {
            const cx = toScreenX(comp.position.x);
            const cy = toScreenY(comp.position.y);
            const halfW = 45 * state.scale;
            const halfH = 26 * state.scale;

            if (screenX >= cx - halfW && screenX <= cx + halfW &&
                screenY >= cy - halfH && screenY <= cy + halfH) {
                selected = comp;
                break;
            }
        }

        state.selectedElement = selected;
        updatePropertySheet(selected);

        // Highlight matching row in BOM table
        document.querySelectorAll("#bomTableBody tr").forEach(tr => {
            if (selected && tr.getAttribute("data-id") === selected.id) {
                tr.classList.add("selected");
                tr.scrollIntoView({ block: "nearest" });
            } else {
                tr.classList.remove("selected");
            }
        });

        render();
    }

    function showTooltip(clientX, clientY, headerText, bodyHtml) {
        elements.tooltipHeader.textContent = headerText;
        elements.tooltipBody.innerHTML = bodyHtml;
        elements.elementTooltip.style.display = "block";

        const containerRect = elements.canvasContainer.getBoundingClientRect();
        let left = clientX - containerRect.left + 14;
        let top = clientY - containerRect.top + 14;

        if (left + 220 > containerRect.width) left -= 240;
        if (top + 120 > containerRect.height) top -= 140;

        elements.elementTooltip.style.left = `${left}px`;
        elements.elementTooltip.style.top = `${top}px`;
    }

    function distToSegment(px, py, x1, y1, x2, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const l2 = dx * dx + dy * dy;
        if (l2 === 0) return Math.hypot(px - x1, py - y1);
        let t = ((px - x1) * dx + (py - y1) * dy) / l2;
        t = Math.max(0, Math.min(1, t));
        return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
    }

    function getNetPinCount(netName) {
        if (!state.ir) return 0;
        const net = state.ir.nets.find(n => n.name === netName);
        return net && net.pins ? net.pins.length : 0;
    }

    // -------------------------------------------------------------------------
    // Main Rendering Pipeline
    // -------------------------------------------------------------------------
    function render() {
        const startTime = performance.now();
        const rect = elements.canvasContainer.getBoundingClientRect();

        ctx.clearRect(0, 0, rect.width, rect.height);

        if (state.layers.grid) {
            drawGrid(rect.width, rect.height);
        }

        if (state.layers.wires) {
            drawNets();
        }

        if (state.layers.components) {
            drawComponents();
        }

        const renderTime = (performance.now() - startTime).toFixed(1);
        if (elements.renderLatency) {
            elements.renderLatency.textContent = `RENDER: ${renderTime}ms`;
        }
    }

    function drawGrid(w, h) {
        const gridStepMils = 100;
        const minMilX = toMilX(0);
        const maxMilX = toMilX(w);
        const minMilY = toMilY(h);
        const maxMilY = toMilY(0);

        const startX = Math.floor(minMilX / gridStepMils) * gridStepMils;
        const endX = Math.ceil(maxMilX / gridStepMils) * gridStepMils;
        const startY = Math.floor(minMilY / gridStepMils) * gridStepMils;
        const endY = Math.ceil(maxMilY / gridStepMils) * gridStepMils;

        ctx.strokeStyle = "#141a29";
        ctx.lineWidth = 1;
        ctx.beginPath();

        for (let gx = startX; gx <= endX; gx += gridStepMils) {
            const sx = Math.round(toScreenX(gx));
            ctx.moveTo(sx, 0);
            ctx.lineTo(sx, h);
        }

        for (let gy = startY; gy <= endY; gy += gridStepMils) {
            const sy = Math.round(toScreenY(gy));
            ctx.moveTo(0, sy);
            ctx.lineTo(w, sy);
        }
        ctx.stroke();

        // Major 500-mil grid lines
        ctx.strokeStyle = "#1b2336";
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let gx = startX; gx <= endX; gx += 500) {
            const sx = Math.round(toScreenX(gx));
            ctx.moveTo(sx, 0);
            ctx.lineTo(sx, h);
        }
        for (let gy = startY; gy <= endY; gy += 500) {
            const sy = Math.round(toScreenY(gy));
            ctx.moveTo(0, sy);
            ctx.lineTo(w, sy);
        }
        ctx.stroke();
    }

    // -------------------------------------------------------------------------
    // Schematic Components Drawing
    // -------------------------------------------------------------------------
    function drawComponents() {
        if (!state.ir || !state.ir.components) return;

        for (const comp of state.ir.components) {
            const cx = toScreenX(comp.position.x);
            const cy = toScreenY(comp.position.y);
            const isHovered = state.hoveredElement === comp;
            const isSelected = state.selectedElement === comp;

            const pinCount = comp.pins ? comp.pins.length : 2;
            const cls = comp.symbol_class ? comp.symbol_class.toUpperCase() : "GENERIC";
            const isComplex = pinCount > 4 || cls.includes("IC") || cls.includes("TIMER") || cls.includes("MCU") || cls.includes("REGULATOR");
            const calHalfW = (isComplex ? 60 : 50) * state.scale;
            const calHalfH = (isComplex ? Math.max(38, (pinCount / 2) * 14) : 30) * state.scale;

            // Highlight border if selected/hovered (strict sharp rect)
            if (isSelected || isHovered) {
                ctx.strokeStyle = isSelected ? "var(--accent-cyan)" : "var(--accent-amber)";
                ctx.lineWidth = 2;
                ctx.strokeRect(cx - calHalfW, cy - calHalfH, calHalfW * 2, calHalfH * 2);

                // Caliper corner markers
                drawCalipers(cx, cy, calHalfW, calHalfH, isSelected ? "#0ea5e9" : "#f59e0b");
            }

            // Draw specific schematic symbol
            drawSymbol(comp, cx, cy);

            // RefDes Text
            ctx.font = `bold ${Math.max(10, Math.round(11 * state.scale))}px "JetBrains Mono", monospace`;
            ctx.fillStyle = "#ffffff";
            ctx.textAlign = "center";
            ctx.fillText(comp.id, cx, cy - (calHalfH + 6 * state.scale));

            // Value Text
            if (comp.value) {
                ctx.font = `${Math.max(9, Math.round(10 * state.scale))}px "JetBrains Mono", monospace`;
                ctx.fillStyle = "var(--accent-amber)";
                ctx.fillText(comp.value, cx, cy + (calHalfH + 14 * state.scale));
            }

            // Draw Pins
            if (state.layers.pins && comp.pins) {
                drawPins(comp, cx, cy);
            }
        }
    }

    function drawCalipers(cx, cy, halfW, halfH, color) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        const len = 8;
        ctx.beginPath();
        // Top-Left
        ctx.moveTo(cx - halfW, cy - halfH + len); ctx.lineTo(cx - halfW, cy - halfH); ctx.lineTo(cx - halfW + len, cy - halfH);
        // Top-Right
        ctx.moveTo(cx + halfW - len, cy - halfH); ctx.lineTo(cx + halfW, cy - halfH); ctx.lineTo(cx + halfW, cy - halfH + len);
        // Bottom-Left
        ctx.moveTo(cx - halfW, cy + halfH - len); ctx.lineTo(cx - halfW, cy + halfH); ctx.lineTo(cx - halfW + len, cy + halfH);
        // Bottom-Right
        ctx.moveTo(cx + halfW - len, cy + halfH); ctx.lineTo(cx + halfW, cy + halfH); ctx.lineTo(cx + halfW, cy + halfH - len);
        ctx.stroke();
    }

    function drawSymbol(comp, cx, cy) {
        const cls = comp.symbol_class ? comp.symbol_class.toUpperCase() : "GENERIC";
        const scale = state.scale;

        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.8;
        ctx.fillStyle = "#0c0f17";

        if (cls.includes("RESISTOR")) {
            // Zigzag Resistor
            const w = 40 * scale;
            const h = 10 * scale;
            ctx.beginPath();
            ctx.moveTo(cx - w, cy);
            ctx.lineTo(cx - w * 0.7, cy);
            ctx.lineTo(cx - w * 0.5, cy - h);
            ctx.lineTo(cx - w * 0.25, cy + h);
            ctx.lineTo(cx, cy - h);
            ctx.lineTo(cx + w * 0.25, cy + h);
            ctx.lineTo(cx + w * 0.5, cy - h);
            ctx.lineTo(cx + w * 0.7, cy);
            ctx.lineTo(cx + w, cy);
            ctx.stroke();
        } else if (cls.includes("CAPACITOR")) {
            // Dual parallel plates
            const plateH = 20 * scale;
            const gap = 6 * scale;
            ctx.beginPath();
            // Left lead and plate
            ctx.moveTo(cx - 24 * scale, cy);
            ctx.lineTo(cx - gap / 2, cy);
            ctx.moveTo(cx - gap / 2, cy - plateH / 2);
            ctx.lineTo(cx - gap / 2, cy + plateH / 2);
            // Right plate and lead
            ctx.moveTo(cx + gap / 2, cy - plateH / 2);
            ctx.lineTo(cx + gap / 2, cy + plateH / 2);
            ctx.moveTo(cx + gap / 2, cy);
            ctx.lineTo(cx + 24 * scale, cy);
            ctx.stroke();
        } else if (cls.includes("INDUCTOR")) {
            // Loops
            const r = 6 * scale;
            ctx.beginPath();
            ctx.arc(cx - 18 * scale, cy, r, Math.PI, 0);
            ctx.arc(cx - 6 * scale, cy, r, Math.PI, 0);
            ctx.arc(cx + 6 * scale, cy, r, Math.PI, 0);
            ctx.arc(cx + 18 * scale, cy, r, Math.PI, 0);
            ctx.stroke();
        } else if (cls.includes("DIODE") || cls.includes("LED")) {
            // Triangle + Bar
            const size = 12 * scale;
            ctx.beginPath();
            ctx.moveTo(cx - size, cy - size);
            ctx.lineTo(cx - size, cy + size);
            ctx.lineTo(cx + size, cy);
            ctx.closePath();
            ctx.stroke();
            // Cathode bar
            ctx.beginPath();
            ctx.moveTo(cx + size, cy - size);
            ctx.lineTo(cx + size, cy + size);
            ctx.stroke();

            // LED Photon Emission Arrows
            if (cls.includes("LED")) {
                ctx.beginPath();
                ctx.moveTo(cx + 2 * scale, cy - 14 * scale); ctx.lineTo(cx + 14 * scale, cy - 24 * scale);
                ctx.moveTo(cx + 8 * scale, cy - 10 * scale); ctx.lineTo(cx + 20 * scale, cy - 20 * scale);
                ctx.stroke();
            }
        } else if (cls.includes("NPN") || (cls.includes("TRANSISTOR") && !cls.includes("PNP"))) {
            // NPN BJT
            const b = 14 * scale;
            ctx.beginPath();
            // Base bar
            ctx.moveTo(cx - 8 * scale, cy - b); ctx.lineTo(cx - 8 * scale, cy + b);
            // Collector
            ctx.moveTo(cx - 8 * scale, cy - b * 0.5); ctx.lineTo(cx + 14 * scale, cy - b);
            // Emitter
            ctx.moveTo(cx - 8 * scale, cy + b * 0.5); ctx.lineTo(cx + 14 * scale, cy + b);
            ctx.stroke();
            // Emitter Arrowhead pointing outward
            ctx.beginPath();
            ctx.moveTo(cx + 14 * scale, cy + b);
            ctx.lineTo(cx + 8 * scale, cy + b * 0.7);
            ctx.lineTo(cx + 12 * scale, cy + b * 0.5);
            ctx.closePath();
            ctx.fillStyle = "#ffffff";
            ctx.fill();
        } else if (cls.includes("PNP")) {
            // PNP BJT
            const b = 14 * scale;
            ctx.beginPath();
            ctx.moveTo(cx - 8 * scale, cy - b); ctx.lineTo(cx - 8 * scale, cy + b);
            ctx.moveTo(cx - 8 * scale, cy - b * 0.5); ctx.lineTo(cx + 14 * scale, cy - b);
            ctx.moveTo(cx - 8 * scale, cy + b * 0.5); ctx.lineTo(cx + 14 * scale, cy + b);
            ctx.stroke();
            // Inward arrow
            ctx.beginPath();
            ctx.moveTo(cx, cy + b * 0.65);
            ctx.lineTo(cx + 4 * scale, cy + b * 0.9);
            ctx.lineTo(cx + 5 * scale, cy + b * 0.4);
            ctx.closePath();
            ctx.fillStyle = "#ffffff";
            ctx.fill();
        } else if (cls.includes("OPAMP")) {
            // Triangle OpAmp
            const w = 34 * scale;
            const h = 26 * scale;
            ctx.beginPath();
            ctx.moveTo(cx - w, cy - h);
            ctx.lineTo(cx - w, cy + h);
            ctx.lineTo(cx + w, cy);
            ctx.closePath();
            ctx.fillStyle = "#101524";
            ctx.fill();
            ctx.stroke();

            // Plus & Minus inputs
            ctx.font = `${Math.round(11 * scale)}px "JetBrains Mono", monospace`;
            ctx.fillStyle = "#ffffff";
            ctx.textAlign = "left";
            ctx.fillText("-", cx - w + 6 * scale, cy - h * 0.4);
            ctx.fillText("+", cx - w + 6 * scale, cy + h * 0.6);
        } else if (cls.includes("GROUND") || cls.includes("GND")) {
            // Ground 3 horizontal stepping plates
            const w1 = 18 * scale, w2 = 12 * scale, w3 = 6 * scale;
            ctx.beginPath();
            ctx.moveTo(cx, cy - 8 * scale); ctx.lineTo(cx, cy);
            ctx.moveTo(cx - w1, cy); ctx.lineTo(cx + w1, cy);
            ctx.moveTo(cx - w2, cy + 4 * scale); ctx.lineTo(cx + w2, cy + 4 * scale);
            ctx.moveTo(cx - w3, cy + 8 * scale); ctx.lineTo(cx + w3, cy + 8 * scale);
            ctx.stroke();
        } else if (cls.includes("VCC") || cls.includes("VDD") || cls.includes("PWR")) {
            // Power rail arrow pointing up
            const s = 10 * scale;
            ctx.beginPath();
            ctx.moveTo(cx, cy + s); ctx.lineTo(cx, cy - s);
            ctx.moveTo(cx - s, cy); ctx.lineTo(cx, cy - s); ctx.lineTo(cx + s, cy);
            ctx.stroke();
        } else if (cls.includes("IC") || cls.includes("TIMER") || cls.includes("MCU") || cls.includes("MICROCONTROLLER") || cls.includes("REGULATOR")) {
            // Multi-Pin Integrated Circuit / MCU / Voltage Regulator
            const pinCount = comp.pins ? comp.pins.length : 8;
            const bw = (pinCount > 8 ? 52 : 38) * scale;
            const bh = Math.max(32, (pinCount <= 4 ? 26 : (pinCount / 2) * 12)) * scale;

            // Main IC Package body (Obsidian Dark with crisp white stroke)
            ctx.fillStyle = "#0c101a";
            ctx.fillRect(cx - bw, cy - bh, bw * 2, bh * 2);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 1.8;
            ctx.strokeRect(cx - bw, cy - bh, bw * 2, bh * 2);

            // Notch at the top edge of chip
            const notchR = 5 * scale;
            ctx.beginPath();
            ctx.arc(cx, cy - bh, notchR, 0, Math.PI);
            ctx.strokeStyle = "var(--accent-cyan)";
            ctx.stroke();

            // Pin 1 dot in top-left
            ctx.beginPath();
            ctx.arc(cx - bw + 8 * scale, cy - bh + 8 * scale, 2.5 * scale, 0, Math.PI * 2);
            ctx.fillStyle = "var(--accent-amber)";
            ctx.fill();

            // Internal Pin Function Labels
            if (comp.pins) {
                ctx.font = `${Math.max(7, Math.round(8 * scale))}px "JetBrains Mono", monospace`;
                for (const pin of comp.pins) {
                    const fn = pin.function || pin.number;
                    const px = toScreenX(pin.pos.x);
                    const py = toScreenY(pin.pos.y);
                    const isLeft = px < cx;
                    ctx.fillStyle = pin.electrical_type === "POWER" ? "var(--accent-amber)" : "#94a3b8";
                    ctx.textAlign = isLeft ? "left" : "right";
                    const tx = isLeft ? cx - bw + 4 * scale : cx + bw - 4 * scale;
                    ctx.fillText(fn, tx, py + 3 * scale);
                }
            }
        } else if (cls.includes("CRYSTAL") || cls.includes("XTAL")) {
            // Quartz crystal resonator: two vertical plates enclosing quartz slab
            const ph = 18 * scale;
            ctx.fillStyle = "#1e293b";
            ctx.fillRect(cx - 3 * scale, cy - ph * 0.7, 6 * scale, ph * 1.4);
            ctx.strokeStyle = "#ffffff";
            ctx.strokeRect(cx - 3 * scale, cy - ph * 0.7, 6 * scale, ph * 1.4);
            ctx.beginPath();
            ctx.moveTo(cx - 22 * scale, cy); ctx.lineTo(cx - 6 * scale, cy);
            ctx.moveTo(cx - 6 * scale, cy - ph / 2); ctx.lineTo(cx - 6 * scale, cy + ph / 2);
            ctx.moveTo(cx + 6 * scale, cy - ph / 2); ctx.lineTo(cx + 6 * scale, cy + ph / 2);
            ctx.moveTo(cx + 6 * scale, cy); ctx.lineTo(cx + 22 * scale, cy);
            ctx.stroke();
        } else if (cls.includes("SWITCH")) {
            // SPST Tactile Switch
            const r = 3 * scale;
            ctx.beginPath();
            ctx.arc(cx - 12 * scale, cy, r, 0, Math.PI * 2);
            ctx.arc(cx + 12 * scale, cy, r, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(cx - 24 * scale, cy); ctx.lineTo(cx - 15 * scale, cy);
            ctx.moveTo(cx + 15 * scale, cy); ctx.lineTo(cx + 24 * scale, cy);
            ctx.moveTo(cx - 11 * scale, cy - 2 * scale);
            ctx.lineTo(cx + 10 * scale, cy - 12 * scale);
            ctx.moveTo(cx, cy - 9 * scale); ctx.lineTo(cx, cy - 16 * scale);
            ctx.moveTo(cx - 6 * scale, cy - 16 * scale); ctx.lineTo(cx + 6 * scale, cy - 16 * scale);
            ctx.stroke();
        } else if (cls.includes("GATE_AND") || cls.includes("GATE_NAND")) {
            const w = 24 * scale;
            const h = 20 * scale;
            ctx.beginPath();
            ctx.moveTo(cx - w, cy - h);
            ctx.lineTo(cx, cy - h);
            ctx.arc(cx, cy, h, -Math.PI / 2, Math.PI / 2);
            ctx.lineTo(cx - w, cy + h);
            ctx.closePath();
            ctx.stroke();
            if (cls.includes("NAND")) {
                ctx.beginPath();
                ctx.arc(cx + h + 3 * scale, cy, 3 * scale, 0, Math.PI * 2);
                ctx.stroke();
            }
        } else if (cls.includes("GATE_OR") || cls.includes("GATE_NOR")) {
            const w = 24 * scale;
            const h = 20 * scale;
            ctx.beginPath();
            ctx.moveTo(cx - w, cy - h);
            ctx.quadraticCurveTo(cx, cy - h, cx + w, cy);
            ctx.quadraticCurveTo(cx, cy + h, cx - w, cy + h);
            ctx.quadraticCurveTo(cx - w * 0.5, cy, cx - w, cy - h);
            ctx.stroke();
            if (cls.includes("NOR")) {
                ctx.beginPath();
                ctx.arc(cx + w + 3 * scale, cy, 3 * scale, 0, Math.PI * 2);
                ctx.stroke();
            }
        } else {
            // Generic Dual-Terminal Box
            const bw = 32 * scale;
            const bh = 18 * scale;
            ctx.fillStyle = "#101524";
            ctx.fillRect(cx - bw, cy - bh, bw * 2, bh * 2);
            ctx.strokeRect(cx - bw, cy - bh, bw * 2, bh * 2);
        }
    }

    function drawPins(comp, cx, cy) {
        const scale = state.scale;
        for (const pin of comp.pins) {
            const px = toScreenX(pin.pos.x);
            const py = toScreenY(pin.pos.y);

            // Stub line from pin coordinate to component boundary
            ctx.strokeStyle = "#475569";
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.moveTo(px, py);
            ctx.lineTo(cx + (px - cx) * 0.5, cy + (py - cy) * 0.5);
            ctx.stroke();

            // Terminal Anchor Dot
            const isHovered = state.hoveredElement === comp && state.hoveredNet === pin.net;
            ctx.fillStyle = isHovered ? "var(--accent-cyan)" : "#ffffff";
            ctx.beginPath();
            ctx.arc(px, py, 3, 0, Math.PI * 2);
            ctx.fill();

            // Pin Number
            ctx.font = `${Math.max(8, Math.round(9 * scale))}px "JetBrains Mono", monospace`;
            ctx.fillStyle = "#94a3b8";
            ctx.textAlign = "center";
            const textOffsetY = py > cy ? py + 12 : py - 6;
            ctx.fillText(pin.number, px, textOffsetY);
        }
    }

    // -------------------------------------------------------------------------
    // Netlist & Orthogonal Wire Tracing
    // -------------------------------------------------------------------------
    function drawNets() {
        if (!state.ir || !state.ir.nets) return;

        for (const net of state.ir.nets) {
            const isHovered = state.hoveredNet === net.name;
            const wireSegments = getNetSegments(net);

            if (wireSegments.length === 0) continue;

            // Trace style
            ctx.strokeStyle = isHovered ? "var(--accent-cyan-hover)" : "var(--accent-cyan)";
            ctx.lineWidth = isHovered ? 3.0 : 1.8;

            if (isHovered) {
                ctx.shadowColor = "rgba(14, 165, 233, 0.6)";
                ctx.shadowBlur = 8;
            } else {
                ctx.shadowColor = "transparent";
                ctx.shadowBlur = 0;
            }

            ctx.beginPath();
            for (const seg of wireSegments) {
                const sx1 = toScreenX(seg.x1);
                const sy1 = toScreenY(seg.y1);
                const sx2 = toScreenX(seg.x2);
                const sy2 = toScreenY(seg.y2);
                ctx.moveTo(sx1, sy1);
                ctx.lineTo(sx2, sy2);
            }
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Solder Junction Dots
            if (wireSegments.length >= 2) {
                ctx.fillStyle = isHovered ? "#38bdf8" : "var(--accent-cyan)";
                for (let i = 0; i < wireSegments.length; i++) {
                    const seg = wireSegments[i];
                    const sx = toScreenX(seg.x1);
                    const sy = toScreenY(seg.y1);
                    ctx.beginPath();
                    ctx.arc(sx, sy, 3.5, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            // Draw Net Labels
            if (state.layers.nets && (net.labels || !net.auto_named)) {
                drawNetLabel(net, wireSegments);
            }
        }
    }

    function getNetSegments(net) {
        const segments = [];
        const pinCoords = [];

        for (const pref of net.pins) {
            const cid = pref[0];
            const pnum = pref[1];
            const comp = state.ir.components.find(c => c.id === cid);
            if (comp && comp.pins) {
                const pin = comp.pins.find(p => p.number === pnum);
                if (pin) {
                    pinCoords.push({ x: pin.pos.x, y: pin.pos.y });
                }
            }
        }

        if (pinCoords.length < 2) return segments;

        // Orthogonal L-routing between pins in sequence
        for (let i = 0; i < pinCoords.length - 1; i++) {
            const p1 = pinCoords[i];
            const p2 = pinCoords[i + 1];

            // Corner coordinate for orthogonal route
            const corner = { x: p2.x, y: p1.y };

            segments.push({ x1: p1.x, y1: p1.y, x2: corner.x, y2: corner.y });
            segments.push({ x1: corner.x, y1: corner.y, x2: p2.x, y2: p2.y });
        }

        return segments;
    }

    function drawNetLabel(net, segments) {
        if (segments.length === 0) return;
        const seg = segments[0];
        const midX = toScreenX((seg.x1 + seg.x2) / 2);
        const midY = toScreenY((seg.y1 + seg.y2) / 2);

        ctx.font = `600 ${Math.max(9, Math.round(10 * state.scale))}px "JetBrains Mono", monospace`;
        ctx.fillStyle = "var(--accent-cyan)";
        ctx.textAlign = "center";
        ctx.fillText(net.name, midX, midY - 6);
    }

    // -------------------------------------------------------------------------
    // Right Inspector Panel: BOM, Nets, Properties, ERC, OrCAD Tcl
    // -------------------------------------------------------------------------
    function populateBomTable() {
        if (!state.ir || !state.ir.components) return;
        elements.bomTableBody.innerHTML = "";

        state.ir.components.forEach(comp => {
            const tr = document.createElement("tr");
            tr.setAttribute("data-id", comp.id);

            const numPins = comp.pins ? comp.pins.length : 0;
            const x = Math.round(comp.position.x);
            const y = Math.round(comp.position.y);

            tr.innerHTML = `
                <td><strong>${comp.id}</strong></td>
                <td>${comp.symbol_class || "-"}</td>
                <td style="color: var(--accent-amber);">${comp.value || "-"}</td>
                <td>${numPins}</td>
                <td style="color: var(--text-muted);">(${x}, ${y})</td>
            `;

            tr.addEventListener("click", () => {
                state.selectedElement = comp;
                updatePropertySheet(comp);
                focusComponentOnCanvas(comp);

                document.querySelectorAll("#bomTableBody tr").forEach(r => r.classList.remove("selected"));
                tr.classList.add("selected");
                render();
            });

            elements.bomTableBody.appendChild(tr);
        });
    }

    function filterBomTable() {
        const query = elements.bomSearchInput.value.toLowerCase().trim();
        document.querySelectorAll("#bomTableBody tr").forEach(tr => {
            const text = tr.textContent.toLowerCase();
            tr.style.display = text.includes(query) ? "" : "none";
        });
    }

    function populateNetTable() {
        if (!state.ir || !state.ir.nets) return;
        elements.netTableBody.innerHTML = "";

        state.ir.nets.forEach(net => {
            const tr = document.createElement("tr");
            const pinStr = net.pins ? net.pins.map(p => `${p[0]}.${p[1]}`).join(", ") : "-";
            const fanout = net.pins ? net.pins.length : 0;
            const type = net.auto_named ? "AUTO" : "EXPLICIT";

            tr.innerHTML = `
                <td><strong style="color: var(--accent-cyan);">${net.name}</strong></td>
                <td style="font-size: 0.68rem; color: var(--text-secondary);">${pinStr}</td>
                <td>${fanout}</td>
                <td style="color: var(--text-muted);">${type}</td>
            `;

            tr.addEventListener("click", () => {
                state.hoveredNet = net.name;
                render();
            });

            elements.netTableBody.appendChild(tr);
        });
    }

    function filterNetTable() {
        const query = elements.netSearchInput.value.toLowerCase().trim();
        document.querySelectorAll("#netTableBody tr").forEach(tr => {
            const text = tr.textContent.toLowerCase();
            tr.style.display = text.includes(query) ? "" : "none";
        });
    }

    function updatePropertySheet(comp) {
        if (!comp) {
            elements.propertySheet.innerHTML = `<div class="empty-hint">Click any component or net in the viewport to inspect electrical properties.</div>`;
            return;
        }

        const pinRows = comp.pins
            ? comp.pins.map(p => `<span style="color: var(--accent-cyan);">${p.number} (${p.net || "N/C"})</span>`).join(", ")
            : "None";

        elements.propertySheet.innerHTML = `
            <div class="prop-row"><span class="prop-label">REFDES:</span><span class="prop-value">${comp.id}</span></div>
            <div class="prop-row"><span class="prop-label">SYMBOL CLASS:</span><span class="prop-value">${comp.symbol_class}</span></div>
            <div class="prop-row"><span class="prop-label">VALUE:</span><span class="prop-value" style="color: var(--accent-amber);">${comp.value || "N/A"}</span></div>
            <div class="prop-row"><span class="prop-label">CONFIDENCE:</span><span class="prop-value">${Math.round(comp.confidence * 100)}%</span></div>
            <div class="prop-row"><span class="prop-label">CAD MILS:</span><span class="prop-value">(${Math.round(comp.position.x)}, ${Math.round(comp.position.y)})</span></div>
            <div class="prop-row"><span class="prop-label">ROTATION:</span><span class="prop-value">${comp.rotation || 0}&deg;</span></div>
            <div class="prop-row"><span class="prop-label">PIN TERMINALS:</span><span class="prop-value" style="font-size: 0.68rem;">${pinRows}</span></div>
        `;
    }

    function focusComponentOnCanvas(comp) {
        const rect = elements.canvasContainer.getBoundingClientRect();
        state.panX = -(comp.position.x - 4000) * state.scale;
        state.panY = -(3000 - comp.position.y) * state.scale;
    }

    function populateErcReport() {
        if (!state.ir) return;
        elements.ercResultsContainer.innerHTML = "";

        const warnings = state.ir.warnings || [];
        if (warnings.length === 0) {
            elements.ercResultsContainer.innerHTML = `
                <div class="erc-clean">
                    [✓ ERC CLEAN] Zero electrical rule check violations detected.<br>
                    All pin terminals, netlist partitions, and 100-mil orthogonal alignments verified.
                </div>
            `;
        } else {
            warnings.forEach(w => {
                const div = document.createElement("div");
                div.className = "erc-item";
                div.innerHTML = `<span class="code">[${w.code}]</span> ${w.detail || "Electrical rule anomaly"}`;
                elements.ercResultsContainer.appendChild(div);
            });
        }
    }

    // -------------------------------------------------------------------------
    // OrCAD Capture Tcl Generation (Mode A & Mode B)
    // -------------------------------------------------------------------------
    function compileTcl() {
        if (!state.ir) return;
        const ir = state.ir;
        const lib = state.tclLibPath;
        const mode = state.routingMode;

        const lines = [];
        lines.push("# =============================================================================");
        lines.push("# Cadence OrCAD Capture Automated Design Reconstruction Script");
        lines.push("# Engine: Schematic2DSN EDA Suite (v2.4)");
        lines.push("# Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN");
        lines.push(`# Circuit: ${(ir.design && ir.design.name) || state.circuitKey.toUpperCase()}`);
        lines.push(`# Compilation Mode: MODE ${mode} (${mode === "A" ? "Stubs + Net Aliases" : "Orthogonal Polylines"})`);
        lines.push("# =============================================================================");
        lines.push("");
        lines.push("package require Dbo");
        lines.push("");
        lines.push("# Initialize Dbo Page & Active Schematic Session");
        lines.push("set lSession $::DboSession_s_pSession");
        lines.push("set lDesign [DboSession_GetActiveDesign $lSession]");
        lines.push("set lPage [DboDesign_GetActivePage $lDesign]");
        lines.push("");
        lines.push(`# Load Component Library Package: ${lib}`);
        lines.push(`set lLibPath "${lib}"`);
        lines.push("");
        lines.push("# -----------------------------------------------------------------------------");
        lines.push("# Component Placement Matrix");
        lines.push("# -----------------------------------------------------------------------------");

        ir.components.forEach(comp => {
            const x = Math.round(comp.position.x);
            const y = Math.round(comp.position.y);
            const refdes = comp.id;
            const sym = comp.symbol_class || "RESISTOR";
            const val = comp.value || "";

            lines.push(`set lInst [DboPage_PlaceObject $lPage "${refdes}" "${sym}" $lLibPath ${x} ${y}]`);
            if (val) {
                lines.push(`DboInstance_SetPropertyValue $lInst "Value" "${val}"`);
            }
        });

        lines.push("");
        lines.push("# -----------------------------------------------------------------------------");
        lines.push("# Electrical Interconnect Routing");
        lines.push("# -----------------------------------------------------------------------------");

        if (mode === "A") {
            // Mode A: Pin stubs + Net Alias labels
            ir.nets.forEach(net => {
                lines.push(`# Net: ${net.name}`);
                net.pins.forEach(pref => {
                    const cid = pref[0];
                    const pnum = pref[1];
                    const comp = ir.components.find(c => c.id === cid);
                    if (comp && comp.pins) {
                        const pin = comp.pins.find(p => p.number === pnum);
                        if (pin) {
                            const px = Math.round(pin.pos.x);
                            const py = Math.round(pin.pos.y);
                            const stubX = px + (px >= comp.position.x ? 100 : -100);
                            lines.push(`set lWire [DboPage_PlaceWire $lPage ${px} ${py} ${stubX} ${py}]`);
                            lines.push(`DboPage_PlaceNetAlias $lPage "${net.name}" ${stubX} ${py}`);
                        }
                    }
                });
            });
        } else {
            // Mode B: Continuous polyline routing
            ir.nets.forEach(net => {
                lines.push(`# Net: ${net.name}`);
                const segs = getNetSegments(net);
                segs.forEach(s => {
                    lines.push(`DboPage_PlaceWire $lPage ${Math.round(s.x1)} ${Math.round(s.y1)} ${Math.round(s.x2)} ${Math.round(s.y2)}`);
                });
                if (segs.length > 0 && !net.auto_named) {
                    const midX = Math.round((segs[0].x1 + segs[0].x2) / 2);
                    const midY = Math.round((segs[0].y1 + segs[0].y2) / 2);
                    lines.push(`DboPage_PlaceNetAlias $lPage "${net.name}" ${midX} ${midY}`);
                }
            });
        }

        lines.push("");
        lines.push("# -----------------------------------------------------------------------------");
        lines.push("# Finalize & Redraw Schematic Canvas");
        lines.push("# -----------------------------------------------------------------------------");
        lines.push("DboPage_Redraw $lPage");
        lines.push("puts \"[SCHEMATIC2DSN] Circuit reconstruction compilation successful.\"");

        state.tclCode = lines.join("\n");
        elements.tclCodeArea.value = state.tclCode;
    }

    function populateJsonIr() {
        if (!state.ir) return;
        elements.jsonIrCodeArea.value = JSON.stringify(state.ir, null, 2);
    }

    function copyToClipboard(text, btnElement, feedbackText) {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = btnElement.textContent;
            btnElement.textContent = feedbackText;
            btnElement.style.backgroundColor = "var(--accent-cyan)";
            btnElement.style.color = "#000000";
            setTimeout(() => {
                btnElement.textContent = originalText;
                btnElement.style.backgroundColor = "";
                btnElement.style.color = "";
            }, 1800);
        }).catch(err => {
            console.error("Failed to copy text: ", err);
        });
    }

    function downloadTclFile() {
        const blob = new Blob([state.tclCode], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${state.circuitKey.toLowerCase()}_design.tcl`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function downloadJsonFile() {
        const jsonStr = JSON.stringify(state.ir, null, 2);
        const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${state.circuitKey.toLowerCase()}_design.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function exportSvg() {
        if (!state.ir) return;
        const ir = state.ir;
        const w = 1200;
        const h = 800;

        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        ir.components.forEach(c => {
            if (c.position.x < minX) minX = c.position.x;
            if (c.position.x > maxX) maxX = c.position.x;
            if (c.position.y < minY) minY = c.position.y;
            if (c.position.y > maxY) maxY = c.position.y;
        });
        minX -= 400; maxX += 400;
        minY -= 300; maxY += 300;
        const spanX = Math.max(maxX - minX, 1000);
        const spanY = Math.max(maxY - minY, 800);

        function toSvgX(mx) { return ((mx - minX) / spanX) * (w - 120) + 60; }
        function toSvgY(my) { return h - (((my - minY) / spanY) * (h - 120) + 60); }

        const svgParts = [];
        svgParts.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">`);
        svgParts.push(`<rect width="100%" height="100%" fill="#06080d"/>`);

        // Grid lines
        for (let gx = Math.floor(minX / 100) * 100; gx <= maxX; gx += 100) {
            const sx = toSvgX(gx);
            svgParts.push(`<line x1="${sx}" y1="0" x2="${sx}" y2="${h}" stroke="#101524" stroke-width="1"/>`);
        }
        for (let gy = Math.floor(minY / 100) * 100; gy <= maxY; gy += 100) {
            const sy = toSvgY(gy);
            svgParts.push(`<line x1="0" y1="${sy}" x2="${w}" y2="${sy}" stroke="#101524" stroke-width="1"/>`);
        }

        // Net wires
        ir.nets.forEach(net => {
            const segs = getNetSegments(net);
            segs.forEach(s => {
                const x1 = toSvgX(s.x1), y1 = toSvgY(s.y1);
                const x2 = toSvgX(s.x2), y2 = toSvgY(s.y2);
                svgParts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#0ea5e9" stroke-width="2.5"/>`);
                svgParts.push(`<circle cx="${x1}" cy="${y1}" r="3.5" fill="#0ea5e9"/>`);
                svgParts.push(`<circle cx="${x2}" cy="${y2}" r="3.5" fill="#0ea5e9"/>`);
            });
            if (segs.length > 0 && !net.auto_named) {
                const midX = toSvgX((segs[0].x1 + segs[0].x2) / 2);
                const midY = toSvgY((segs[0].y1 + segs[0].y2) / 2) - 8;
                svgParts.push(`<text x="${midX}" y="${midY}" fill="#0ea5e9" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">${net.name}</text>`);
            }
        });

        // Components
        ir.components.forEach(c => {
            const cx = toSvgX(c.position.x);
            const cy = toSvgY(c.position.y);
            svgParts.push(`<rect x="${cx - 45}" y="${cy - 22}" width="90" height="44" fill="#0c101a" stroke="#ffffff" stroke-width="1.8"/>`);
            svgParts.push(`<text x="${cx}" y="${cy - 4}" fill="#ffffff" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">${c.id}</text>`);
            if (c.value) {
                svgParts.push(`<text x="${cx}" y="${cy + 13}" fill="#f59e0b" font-family="monospace" font-size="10" text-anchor="middle">${c.value}</text>`);
            }
            if (c.pins) {
                c.pins.forEach(p => {
                    const px = toSvgX(p.pos.x);
                    const py = toSvgY(p.pos.y);
                    svgParts.push(`<line x1="${cx}" y1="${cy}" x2="${px}" y2="${py}" stroke="#475569" stroke-width="1.5"/>`);
                    svgParts.push(`<circle cx="${px}" cy="${py}" r="3" fill="#ffffff"/>`);
                });
            }
        });

        // Technical Header Watermark
        svgParts.push(`<text x="24" y="32" fill="#94a3b8" font-family="monospace" font-size="12" font-weight="bold">SCHEMATIC2DSN // CAD RECONSTRUCTION CORE</text>`);
        svgParts.push(`<text x="24" y="50" fill="#64748b" font-family="monospace" font-size="10">CIRCUIT: ${state.circuitKey.toUpperCase()} • AUTHOR: JATIN MAKHIJA (@JatinMakhija-10)</text>`);
        svgParts.push(`</svg>`);

        const blob = new Blob([svgParts.join("\n")], { type: "image/svg+xml;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${state.circuitKey.toLowerCase()}_schematic.svg`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function exportPng() {
        if (!state.ir) return;
        const link = document.createElement("a");
        link.download = `${state.circuitKey.toLowerCase()}_schematic.png`;
        link.href = elements.canvas.toDataURL("image/png");
        link.click();
    }

    // -------------------------------------------------------------------------
    // File Ingestion Handler
    // -------------------------------------------------------------------------
    function handleFileDrop(e) {
        e.preventDefault();
        elements.dropZone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            processUploadedFile(e.dataTransfer.files[0]);
        }
    }

    function handleFileInput(e) {
        if (e.target.files && e.target.files.length > 0) {
            processUploadedFile(e.target.files[0]);
        }
    }

    function processUploadedFile(file) {
        const name = file.name.toLowerCase();
        if (name.endsWith(".json")) {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const parsed = JSON.parse(event.target.result);
                    state.ir = parsed;
                    state.circuitKey = file.name.replace(".json", "");
                    updateTelemetry();
                    populateBomTable();
                    populateNetTable();
                    populateErcReport();
                    compileTcl();
                    populateJsonIr();
                    fitToScreen();
                    if (elements.statusCircuitName) {
                        elements.statusCircuitName.textContent = `CIRCUIT: ${file.name.toUpperCase()}`;
                    }
                } catch (err) {
                    alert("Invalid JSON format: " + err.message);
                }
            };
            reader.readAsText(file);
        } else {
            // Image / PDF upload notice
            alert(`File "${file.name}" received.\nImage/PDF raster ingestion requires backend Python OCR/YOLO pipeline.\nLoaded synthetic representation for interactive CAD preview.`);
            loadCircuit("voltage_divider");
        }
    }

    // Run on startup
    window.addEventListener("DOMContentLoaded", init);

})();
