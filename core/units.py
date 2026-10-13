"""
core/units.py  --  Value string normalization for component values.

Normalizes strings like '4k7', '.1uF', '10K', 'µ', '2k2' to canonical forms.
"""
from __future__ import annotations

import re

# Normalization maps
_UNIT_MAP = {
    'Ω': 'ohm', 'ohm': 'ohm', 'R': 'ohm',
    'u': 'u', 'µ': 'u', 'μ': 'u', 'U': 'u',
    'K': 'k', 'M': 'M',
    'p': 'p', 'n': 'n', 'f': 'F', 'F': 'F',
}


def normalize_value(raw: str) -> str:
    """
    Normalize a component value string to canonical form.

    Examples
    --------
    normalize_value('4k7')   -> '4.7k'
    normalize_value('.1uF')  -> '0.1uF'
    normalize_value('10K')   -> '10k'
    normalize_value('2k2')   -> '2.2k'
    normalize_value('1µF')   -> '1uF'
    normalize_value('100R')  -> '100ohm'
    """
    s = raw.strip()

    # Replace Unicode ohm and mu variants
    s = s.replace('Ω', 'ohm').replace('µ', 'u').replace('μ', 'u')

    # Leading dot -> '0.'
    s = re.sub(r'^(\.)', '0.', s)

    # 4k7 -> 4.7k, 4R7 -> 4.7ohm  (letter-separated decimal)
    m = re.match(r'^(\d+)([kKmMnNpPuUfFrR])(\d+)([A-Za-zΩ]*)$', s)
    if m:
        int_part, sep, frac, suffix = m.groups()
        if sep in ('k', 'K'):
            sep_norm = 'k'
        elif sep in ('r', 'R'):
            sep_norm = 'ohm'
        else:
            sep_norm = sep
        s = f'{int_part}.{frac}{sep_norm}{suffix}'

    # Suffix R -> ohm (e.g. 100R -> 100ohm)
    s = re.sub(r'^(\d+(?:\.\d+)?)[Rr]$', r'\1ohm', s)

    # Normalize case: K -> k
    s = s.replace('K', 'k')

    return s


REFDES_PATTERN = re.compile(r'^[A-Z]{1,5}[0-9]{1,4}[A-Z]?$')


def validate_refdes(s: str) -> bool:
    """Return True if string is a valid Reference Designator (e.g. R1, C2, XTAL1, U1A)."""
    return bool(REFDES_PATTERN.match(s))

CLASS_PREFIX = {
    'RESISTOR':         {'R'},
    'CAPACITOR':        {'C'},
    'INDUCTOR':         {'L'},
    'DIODE':            {'D'},
    'LED':              {'D', 'LED'},
    'NPN':              {'Q'},
    'PNP':              {'Q'},
    'NMOS':             {'Q', 'M'},
    'PMOS':             {'Q', 'M'},
    'OPAMP':            {'U'},
    'CONNECTOR':        {'J', 'P', 'CONN'},
    'GROUND':           set(),
    'VCC':              set(),
    'IC':               {'U', 'IC'},
    'MICROCONTROLLER':  {'U', 'MCU', 'IC'},
    'MCU':              {'U', 'MCU', 'IC'},
    'TIMER_555':        {'U', 'IC'},
    'REGULATOR':        {'U', 'VR', 'REG'},
    'CRYSTAL':          {'Y', 'X', 'XTAL'},
    'TRANSFORMER':      {'T', 'TR', 'XFMR'},
    'RELAY':            {'K', 'RL', 'RY'},
    'SWITCH':           {'SW', 'S'},
    'GATE_AND':         {'U'},
    'GATE_OR':          {'U'},
    'GATE_NAND':        {'U'},
    'GATE_NOR':         {'U'},
    'GATE_XOR':         {'U'},
    'GATE_NOT':         {'U'},
}


def fix_refdes(raw: str, symbol_class: str | None = None) -> str:
    """
    Apply OCR fixes to a refdes string.
    Only replaces 'O' with '0' and 'l/I' with '1' when the result
    still matches the refdes pattern.
    """
    candidates = [raw]
    # Try common OCR fixes
    fixed = raw.replace('O', '0').replace('l', '1').replace('I', '1')
    candidates.append(fixed)
    for c in candidates:
        if REFDES_PATTERN.match(c):
            if symbol_class:
                prefix = re.match(r'^[A-Z]+', c)
                if prefix and prefix.group() in CLASS_PREFIX.get(symbol_class, set()):
                    return c
            else:
                return c
    return raw  # return unchanged if no valid candidate
