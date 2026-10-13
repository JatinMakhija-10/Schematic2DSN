# Contributing to Schematic2DSN

Thank you for your interest in contributing to **Schematic2DSN**! This project is maintained by **Jatin Makhija** ([@JatinMakhija-10](https://github.com/JatinMakhija-10)).

Repository: [https://github.com/JatinMakhija-10/Schematic2DSN](https://github.com/JatinMakhija-10/Schematic2DSN)

---

## Architecture Principles & Golden Rules

1. **Connectivity via Pin Numbers**: Pin numbers define electrical connectivity; pin labels/names are for display only.
2. **Deterministic Graph Extraction**: Never let an LLM invent or modify connectivity or generate raw Tcl commands.
3. **Pure Function Stages**: Every stage reads standard Pydantic JSON contracts and writes verified outputs + debug overlays.
4. **Coordinate Transformation Isolation**: All conversions between Image Pixels (origin top-left, y down) and OrCAD Capture Mils (origin bottom-left, y up) live exclusively in `core/geometry.py`.
5. **No Magic Numbers**: Thresholds and tolerances belong exclusively in `core/config.py`.
6. **Capture Tcl Verification**: Only use journaled Capture commands verified from OrCAD sessions.

---

## Development Workflow

1. Fork the repository: [https://github.com/JatinMakhija-10/Schematic2DSN/fork](https://github.com/JatinMakhija-10/Schematic2DSN/fork)
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/Schematic2DSN.git
   cd Schematic2DSN
   ```
3. Set up the Python 3.11 environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
4. Run the comprehensive test suite:
   ```bash
   pytest -v
   ```
5. Ensure all 151+ tests pass before opening a Pull Request.

---

## Reporting Issues

Found a bug or have a suggestion? Open an issue on GitHub:
👉 [https://github.com/JatinMakhija-10/Schematic2DSN/issues](https://github.com/JatinMakhija-10/Schematic2DSN/issues)
