# Schematic2DSN Agent Rules

Project: **Schematic2DSN**
Author: **Jatin Makhija** ([@JatinMakhija-10](https://github.com/JatinMakhija-10))
Repository: [https://github.com/JatinMakhija-10/Schematic2DSN](https://github.com/JatinMakhija-10/Schematic2DSN)

Target: Schematic PDF or image in -> native, editable OrCAD Capture design out.

## Core Rules:
1. **Connectivity**: Pin numbers are physical connectivity. Pin labels are for display only.
2. **Deterministic Code**: Never let an LLM invent connectivity or generate raw Tcl. Deterministic code owns the netlist.
3. **Pure Functions**: Each stage reads Pydantic JSON contracts and writes verified JSON outputs + debug PNGs.
4. **Coordinate Conversions**: Lives only in `core/geometry.py`.
5. **Configuration**: Tolerances, thresholds, and magic constants live exclusively in `core/config.py`.
6. **Capture Tcl**: Never invent Capture Tcl commands. Use only verified commands from journaling notes.
7. **Testing**: Run `pytest` before finalizing any changes.
