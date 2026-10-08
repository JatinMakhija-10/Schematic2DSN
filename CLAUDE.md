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

Rule 9 matters most. A coding assistant will confidently invent plausible Tcl that
does not exist in Capture.
