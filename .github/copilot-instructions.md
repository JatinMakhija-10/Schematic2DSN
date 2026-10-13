# GitHub Copilot Instructions for Schematic2DSN

Project: **Schematic2DSN**
Author: **Jatin Makhija** ([@JatinMakhija-10](https://github.com/JatinMakhija-10))
Repository: [https://github.com/JatinMakhija-10/Schematic2DSN](https://github.com/JatinMakhija-10/Schematic2DSN)

## Engineering Rules
1. Connectivity uses pin numbers only (never pin labels/names).
2. All JSON data passes through Pydantic models in `core/models.py`.
3. Coordinate transformation between Image (px) and Capture (mils) lives only in `core/geometry.py`.
4. All tolerances, thresholds, and dimensions live in `core/config.py`.
5. Every stage is a pure function with a CLI entrypoint and debug overlay image generator.
6. Only use verified OrCAD Tcl commands derived from journaling.
7. Test with `pytest` after any bug fix or enhancement.
