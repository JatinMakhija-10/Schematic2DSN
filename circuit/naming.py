"""
circuit/naming.py  --  Stable net and refdes naming conventions.

Ensures deterministic, canonical sorting and stable auto-generated identifiers.
"""
from __future__ import annotations

import re
from typing import List, Set
from core.models import NetIR, ComponentIR


def sort_nets_deterministically(nets: List[NetIR]) -> List[NetIR]:
    """
    Sort nets by label/name, prioritizing explicit user labels, then sorted pin ids.
    """
    def net_sort_key(n: NetIR):
        # Explicitly named first, then alphabetically
        auto_flag = 1 if n.auto_named else 0
        min_pin = min([f"{p[0]}:{p[1]}" for p in n.pins]) if n.pins else ""
        return (auto_flag, n.name, min_pin)

    return sorted(nets, key=net_sort_key)


def generate_stable_net_name(index: int) -> str:
    """Format auto net names like NET_001, NET_002."""
    return f"NET_{index:03d}"


def generate_stable_refdes(symbol_class: str, existing_ids: Set[str]) -> str:
    """
    Generate the next available refdes for a class (e.g. R1, R2 or R_AUTO1).
    """
    from circuit.associate import _class_to_prefix
    prefix = _class_to_prefix(symbol_class)
    idx = 1
    while f"{prefix}{idx}" in existing_ids or f"{prefix}_AUTO{idx}" in existing_ids:
        idx += 1
    return f"{prefix}_AUTO{idx}"
