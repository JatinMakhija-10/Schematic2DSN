"""
tests/test_frontend.py  --  Frontend Aesthetic & Structural Contract Tests.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN

Verifies:
  1. Strict 0px Border Radius constraint across all web styling.
  2. Absolute absence of purple and green hues across styles.
  3. Proper GitHub and author attribution across web artifacts.
  4. Complete benchmark circuits bundle availability (all 9 circuits).
  5. Interactive EDA symbol rendering and OrCAD Tcl compiler routines in app.js.
"""
from __future__ import annotations

import re
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent.parent / "app" / "web"


def test_frontend_files_exist():
    assert (WEB_DIR / "index.html").exists(), "index.html missing"
    assert (WEB_DIR / "index.css").exists(), "index.css missing"
    assert (WEB_DIR / "app.js").exists(), "app.js missing"
    assert (WEB_DIR / "circuits.js").exists(), "circuits.js missing"


def test_zero_round_corners_enforced():
    css_content = (WEB_DIR / "index.css").read_text(encoding="utf-8")
    assert "border-radius: 0px !important;" in css_content, "Global 0px border-radius reset missing in CSS"

    # Ensure no positive border-radius values exist
    positive_radius = re.findall(r"border-radius:\s*([1-9]\d*px|[0-9\.]+rem|[0-9\.]+%|[0-9\.]+em)", css_content)
    assert len(positive_radius) == 0, f"Found forbidden rounded corners: {positive_radius}"


def test_no_purple_no_green_in_css():
    css_content = (WEB_DIR / "index.css").read_text(encoding="utf-8").lower()
    # Strip all CSS block comments
    code_text = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)

    forbidden_colors = [
        "purple", "violet", "indigo", "magenta",
        "#8a2be2", "#9333ea", "#a855f7", "#7c3aed", "#6366f1", "#4f46e5", "#800080",
        "lime", "#00ff00", "#10b981", "#22c55e", "#16a34a", "#15803d", "#84cc16"
    ]

    for color in forbidden_colors:
        assert color not in code_text, f"Forbidden color detected in CSS: {color}"


def test_circuits_bundle_complete():
    circuits_js = (WEB_DIR / "circuits.js").read_text(encoding="utf-8")
    expected_circuits = [
        "voltage_divider",
        "rc_filter",
        "led_driver",
        "inverting_opamp",
        "common_emitter",
        "bjt_astable",
        "h_bridge",
        "diff_amp",
        "bandpass_filter",
        "timer_555_astable",
        "buck_converter",
        "mcu_minimum_system",
    ]
    for c in expected_circuits:
        assert f'"{c}"' in circuits_js, f"Benchmark circuit '{c}' missing from circuits.js"


def test_github_author_attribution():
    html_content = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    assert "Jatin Makhija" in html_content, "Author name missing in index.html"
    assert "@JatinMakhija-10" in html_content, "GitHub handle missing in index.html"
    assert "https://github.com/JatinMakhija-10/Schematic2DSN" in html_content, "Repo URL missing in index.html"


def test_app_js_features():
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    # Verify core and complex EDA symbol rendering branches exist
    assert "RESISTOR" in app_js
    assert "CAPACITOR" in app_js
    assert "OPAMP" in app_js
    assert "NPN" in app_js
    assert "DIODE" in app_js
    assert "GROUND" in app_js
    assert "VCC" in app_js
    assert "TIMER" in app_js
    assert "MCU" in app_js
    assert "REGULATOR" in app_js
    assert "CRYSTAL" in app_js
    assert "SWITCH" in app_js
    # Verify Mode A & Mode B Tcl generation
    assert "DboPage_PlaceObject" in app_js
    assert "DboPage_PlaceWire" in app_js
    assert "DboPage_PlaceNetAlias" in app_js
    # Verify vector and raster schematic exports
    assert "exportSvg" in app_js
    assert "exportPng" in app_js

