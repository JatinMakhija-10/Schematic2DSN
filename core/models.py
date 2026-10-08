"""
core/models.py  --  Pydantic data contracts for Schematic2DSN.

Schema version: 1.0
Never change a field without bumping the schema version constant and updating tests.
"""
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared primitives
# ---------------------------------------------------------------------------

class Point(BaseModel):
    x: float
    y: float


class BBox(BaseModel):
    """Axis-aligned bounding box in pixels (image coordinates)."""
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    def expanded(self, px: float) -> 'BBox':
        return BBox(x0=self.x0 - px, y0=self.y0 - px,
                    x1=self.x1 + px, y1=self.y1 + px)

    def contains(self, p: Point) -> bool:
        return self.x0 <= p.x <= self.x1 and self.y0 <= p.y <= self.y1


# ---------------------------------------------------------------------------
# S1 Ingest  ->  page.meta.json
# ---------------------------------------------------------------------------

SCHEMA_PAGE_META = "1.0"


class PageMeta(BaseModel):
    schema_version: str = SCHEMA_PAGE_META
    source: str                        # original file path
    mode: Literal["vector", "raster"]  # extraction mode used
    width_px: int
    height_px: int
    dpi: float
    pixel_per_mil_hint: Optional[float] = None  # from PDF page size
    page_index: int = 0


# ---------------------------------------------------------------------------
# S2 Text  ->  texts.json
# ---------------------------------------------------------------------------

SCHEMA_TEXTS = "1.0"


class TextItem(BaseModel):
    text: str
    bbox: BBox
    angle: float = 0.0    # degrees CCW
    conf: float = 1.0     # 0-1
    source: Literal["vector", "ocr"] = "ocr"


class TextsFile(BaseModel):
    schema_version: str = SCHEMA_TEXTS
    items: List[TextItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# S3 Symbols  ->  symbols.json
# ---------------------------------------------------------------------------

SCHEMA_SYMBOLS = "1.0"

SymbolClass = Literal[
    "RESISTOR", "CAPACITOR", "INDUCTOR", "DIODE", "LED",
    "GROUND", "VCC", "OPAMP", "NPN", "PNP", "NMOS", "PMOS", "CONNECTOR"
]


class SymbolItem(BaseModel):
    id: str                             # e.g. "SYM_001"
    symbol_class: SymbolClass
    bbox: BBox                          # pixels
    rotation: int = 0                   # 0 | 90 | 180 | 270
    mirror: bool = False
    conf: float = 1.0
    source: Literal["cv", "yolo", "llm"] = "cv"
    style: Optional[Literal["ANSI", "IEC"]] = None


class SymbolsFile(BaseModel):
    schema_version: str = SCHEMA_SYMBOLS
    items: List[SymbolItem] = Field(default_factory=list)
    style_flag: Optional[Literal["ANSI", "IEC"]] = None


# ---------------------------------------------------------------------------
# S4 Wires  ->  wires.json
# ---------------------------------------------------------------------------

SCHEMA_WIRES = "1.0"


class WireSegment(BaseModel):
    id: str                             # e.g. "W_001"
    p0: Point                           # pixel coords, integer
    p1: Point

    @property
    def is_horizontal(self) -> bool:
        return abs(self.p0.y - self.p1.y) < abs(self.p0.x - self.p1.x)

    @property
    def is_vertical(self) -> bool:
        return not self.is_horizontal


class WiresFile(BaseModel):
    schema_version: str = SCHEMA_WIRES
    segments: List[WireSegment] = Field(default_factory=list)
    endpoints: List[Point] = Field(default_factory=list)  # deduplicated


# ---------------------------------------------------------------------------
# S5 Junctions  ->  junctions.json
# ---------------------------------------------------------------------------

SCHEMA_JUNCTIONS = "1.0"


class JunctionItem(BaseModel):
    pos: Point
    radius: float


class JunctionsFile(BaseModel):
    schema_version: str = SCHEMA_JUNCTIONS
    items: List[JunctionItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# design.json  --  the IR (Intermediate Representation)
# ---------------------------------------------------------------------------

SCHEMA_DESIGN = "1.0"


class PinIR(BaseModel):
    number: str              # physical pin number (connectivity key)
    function: str            # display name (anode, cathode, base…)
    pos: Point               # position in mils (Capture coords)
    net: Optional[str] = None


class ComponentIR(BaseModel):
    id: str                  # refdes e.g. "R1"
    symbol_class: SymbolClass
    value: str = ""
    unit: int = 1            # for multi-unit packages
    position: Point          # mils, Capture coords
    rotation: int = 0        # 0 | 90 | 180 | 270
    mirror: bool = False
    src_bbox_px: List[float] = Field(default_factory=list)  # [x0,y0,x1,y1]
    confidence: float = 1.0
    pins: List[PinIR] = Field(default_factory=list)


class LabelIR(BaseModel):
    text: str
    pos: Point


class NetIR(BaseModel):
    name: str
    auto_named: bool = True
    pins: List[List[str]] = Field(default_factory=list)  # [[refdes, pin_num]]
    labels: List[LabelIR] = Field(default_factory=list)


class WarningIR(BaseModel):
    code: str
    detail: str = ""
    net: Optional[str] = None
    component: Optional[str] = None


class DesignMetadata(BaseModel):
    source: str
    mode: Literal["vector", "raster"]
    confidence: float
    ocr_confidence: float = 1.0


class DesignInfo(BaseModel):
    name: str = "converted"
    page: int = 1
    units: str = "mils"
    grid: int = 100


class DesignIR(BaseModel):
    """The canonical intermediate representation written by S9 and consumed by S10."""
    schema_version: str = SCHEMA_DESIGN
    design: DesignInfo = Field(default_factory=DesignInfo)
    components: List[ComponentIR] = Field(default_factory=list)
    nets: List[NetIR] = Field(default_factory=list)
    warnings: List[WarningIR] = Field(default_factory=list)
    metadata: Optional[DesignMetadata] = None
