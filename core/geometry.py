"""
core/geometry.py  --  Coordinate transforms (the ONLY place they live).

Coordinate systems:
  - Image (px): origin top-left, y increases downward
  - Capture (mils): origin bottom-left of sheet, y increases upward

All transforms go through px_to_mils() and mils_to_px().
The scale is set once per document based on median passive body length.
"""
from __future__ import annotations

import math
from typing import Tuple

from core.models import Point, BBox


class CoordTransform:
    """
    Holds the scale and origin for one document.

    Parameters
    ----------
    scale_px_per_mil : float
        How many image pixels equal one mil.
    sheet_height_mils : int
        Total sheet height in mils (for y-flip).
    origin_px : Tuple[float, float]
        Image pixel coordinate that maps to Capture (0, 0).
        Typically the bottom-left corner of the schematic area.
    """

    def __init__(
        self,
        scale_px_per_mil: float,
        sheet_height_mils: int = 8500,
        origin_px: Tuple[float, float] = (0.0, 0.0),
    ) -> None:
        if scale_px_per_mil <= 0:
            raise ValueError(f"scale_px_per_mil must be positive, got {scale_px_per_mil}")
        self.scale = scale_px_per_mil
        self.sheet_height_mils = sheet_height_mils
        self.origin_px = origin_px

    # ------------------------------------------------------------------
    # Primary API
    # ------------------------------------------------------------------

    def px_to_mils(self, px_x: float, px_y: float) -> Tuple[float, float]:
        """Convert image pixel coords to Capture mils."""
        rel_x = px_x - self.origin_px[0]
        rel_y = px_y - self.origin_px[1]
        mil_x = rel_x / self.scale
        # y-flip: image y down -> Capture y up
        mil_y = self.sheet_height_mils - (rel_y / self.scale)
        return mil_x, mil_y

    def mils_to_px(self, mil_x: float, mil_y: float) -> Tuple[float, float]:
        """Convert Capture mils back to image pixel coords (round-trip)."""
        rel_y_mils = self.sheet_height_mils - mil_y
        px_x = mil_x * self.scale + self.origin_px[0]
        px_y = rel_y_mils * self.scale + self.origin_px[1]
        return px_x, px_y

    def px_point_to_mils(self, p: Point) -> Point:
        mx, my = self.px_to_mils(p.x, p.y)
        return Point(x=mx, y=my)

    def mils_point_to_px(self, p: Point) -> Point:
        px, py = self.mils_to_px(p.x, p.y)
        return Point(x=px, y=py)

    def snap_to_grid(self, mil_x: float, mil_y: float, grid: int = 100) -> Tuple[int, int]:
        """Snap mils coordinate to the Capture grid."""
        return (round(mil_x / grid) * grid, round(mil_y / grid) * grid)


# ---------------------------------------------------------------------------
# Utility functions (stateless)
# ---------------------------------------------------------------------------

def distance(p1: Point, p2: Point) -> float:
    """Euclidean distance between two points."""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def segment_length(p0: Point, p1: Point) -> float:
    return distance(p0, p1)


def bbox_center(bbox: BBox) -> Point:
    return Point(x=(bbox.x0 + bbox.x1) / 2, y=(bbox.y0 + bbox.y1) / 2)


def rotate_point(p: Point, origin: Point, degrees: float) -> Point:
    """Rotate p around origin by degrees CCW."""
    rad = math.radians(degrees)
    dx = p.x - origin.x
    dy = p.y - origin.y
    nx = dx * math.cos(rad) - dy * math.sin(rad)
    ny = dx * math.sin(rad) + dy * math.cos(rad)
    return Point(x=origin.x + nx, y=origin.y + ny)


def point_on_segment(p: Point, seg_p0: Point, seg_p1: Point, tol: float = 1e-6) -> bool:
    """Return True if p lies on the segment [seg_p0, seg_p1] within tol."""
    d_seg = distance(seg_p0, seg_p1)
    if d_seg < tol:
        return distance(p, seg_p0) < tol
    d_p = distance(seg_p0, p) + distance(p, seg_p1)
    return abs(d_p - d_seg) < tol


def closest_point_on_segment(p: Point, seg_p0: Point, seg_p1: Point) -> Point:
    """Project p onto segment, clamp to endpoints."""
    dx = seg_p1.x - seg_p0.x
    dy = seg_p1.y - seg_p0.y
    len_sq = dx * dx + dy * dy
    if len_sq < 1e-12:
        return seg_p0
    t = ((p.x - seg_p0.x) * dx + (p.y - seg_p0.y) * dy) / len_sq
    t = max(0.0, min(1.0, t))
    return Point(x=seg_p0.x + t * dx, y=seg_p0.y + t * dy)


def estimate_scale_from_passives(
    body_lengths_px: list[float],
    nominal_body_mils: float = 200.0,
) -> float:
    """
    Estimate px_per_mil from measured passive body lengths.
    Uses median to be robust against outliers.
    """
    if not body_lengths_px:
        raise ValueError("body_lengths_px is empty; cannot estimate scale")
    import statistics
    median_px = statistics.median(body_lengths_px)
    return median_px / nominal_body_mils
