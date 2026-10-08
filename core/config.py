"""
core/config.py  --  All thresholds, tolerances, and tunable constants.

Import this module everywhere a numeric threshold is needed.
Never put raw numbers in vision/, circuit/, or orcad/ code.
"""
from __future__ import annotations

from pydantic import BaseModel


class IngestConfig(BaseModel):
    render_dpi: int = 600
    min_vector_paths: int = 10        # PDF paths to qualify as vector
    otsu_block_size: int = 0          # 0 = global Otsu
    speck_min_area_px: int = 6
    max_skew_degrees: float = 2.0
    min_image_long_side_px: int = 1200
    min_dpi_equivalent: float = 200.0
    max_offaxis_fraction: float = 0.05
    max_offaxis_degrees: float = 3.0


class WireConfig(BaseModel):
    hough_min_length_factor: float = 0.6   # fraction of (median_thickness * 8)
    hough_threshold: int = 30
    snap_angle_degrees: float = 5.0        # angles within this -> 0 or 90
    merge_lateral_px: float = 2.0
    merge_gap_px: float = 3.0
    bbox_dilate_px: int = 3               # dilate component bboxes before masking


class JunctionConfig(BaseModel):
    disc_radius_px: int = 4               # morphological opening disc
    min_circularity: float = 0.7
    plus_crossing_requires_dot: bool = True


class PinConfig(BaseModel):
    snap_tolerance_px: float = 6.0        # at 600 DPI; tune per doc
    passive_pin1_side: str = "left_top"   # deterministic assignment


class SymbolConfig(BaseModel):
    min_confidence: float = 0.50
    llm_confidence_threshold: float = 0.80
    resistor_min_turns: int = 6


class GraphConfig(BaseModel):
    label_snap_tolerance_px: float = 8.0
    endpoint_merge_tolerance_px: float = 2.0


class OrcadConfig(BaseModel):
    grid_mils: int = 100
    stub_length_mils: int = 100           # Mode A net alias stub
    default_sheet: str = "A"
    large_sheet: str = "B"
    sheet_sizes_mils: dict = {
        "A": (11000, 8500),
        "B": (17000, 11000),
        "C": (22000, 17000),
        "D": (34000, 22000),
    }


class Config(BaseModel):
    """Top-level config. Load once per run."""
    ingest: IngestConfig = IngestConfig()
    wire: WireConfig = WireConfig()
    junction: JunctionConfig = JunctionConfig()
    pin: PinConfig = PinConfig()
    symbol: SymbolConfig = SymbolConfig()
    graph: GraphConfig = GraphConfig()
    orcad: OrcadConfig = OrcadConfig()


# Module-level singleton
DEFAULT_CONFIG = Config()
