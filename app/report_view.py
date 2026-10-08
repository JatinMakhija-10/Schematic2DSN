"""
app/report_view.py  --  Dedicated validation and confidence report viewer.
"""
from __future__ import annotations

from typing import Dict, Any
from core.models import DesignIR


def generate_markdown_report(ir: DesignIR) -> str:
    """Generate a clean markdown report of the design IR."""
    lines = []
    lines.append(f"# Schematic Reconstruction Report: {ir.design.name}")
    lines.append("")
    conf = ir.metadata.confidence if ir.metadata else 0.0
    lines.append(f"- **Confidence Score**: {conf:.1%}")
    lines.append(f"- **Extraction Mode**: {ir.metadata.mode if ir.metadata else 'unknown'}")
    lines.append(f"- **Total Components**: {len(ir.components)}")
    lines.append(f"- **Total Nets**: {len(ir.nets)}")
    lines.append(f"- **Total Warnings / ERC Flags**: {len(ir.warnings)}")
    lines.append("")

    lines.append("## ERC Warnings & Flags")
    if not ir.warnings:
        lines.append("No warnings or errors detected.")
    else:
        for w in ir.warnings:
            lines.append(f"- `[{w.code}]` {w.detail}")
    lines.append("")

    lines.append("## Components")
    lines.append("| RefDes | Class | Value | Confidence | Pins |")
    lines.append("|---|---|---|---|---|")
    for c in ir.components:
        lines.append(f"| {c.id} | {c.symbol_class} | {c.value or '-'} | {c.confidence:.0%} | {len(c.pins)} |")
    lines.append("")

    lines.append("## Netlist Connections")
    lines.append("| Net | Auto-Named | Connected Pins |")
    lines.append("|---|---|---|")
    for n in ir.nets:
        pin_strs = ", ".join([f"{p[0]}.{p[1]}" for p in n.pins])
        lines.append(f"| {n.name} | {n.auto_named} | {pin_strs} |")

    return "\n".join(lines)
