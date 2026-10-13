"""
tests/test_ingest.py  --  Tests for Stage S1 Ingest module.
Author: Jatin Makhija (@JatinMakhija-10) - https://github.com/JatinMakhija-10/Schematic2DSN
"""
import json
import sys
from pathlib import Path
import pytest
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import PageMeta
from vision.ingest import ingest, IngestError, REJECT_CODES


def test_ingest_rejects_nonexistent_file(tmp_path):
    with pytest.raises(IngestError) as exc_info:
        ingest(str(tmp_path / "does_not_exist.pdf"), str(tmp_path / "out"))
    assert "FILE_NOT_FOUND" in str(exc_info.value)


def test_ingest_rejects_unsupported_extension(tmp_path):
    txt_file = tmp_path / "schematic.txt"
    txt_file.write_text("dummy text")
    with pytest.raises(IngestError) as exc_info:
        ingest(str(txt_file), str(tmp_path / "out"))
    assert "UNSUPPORTED_TYPE" in str(exc_info.value)


def test_ingest_rejects_small_image(tmp_path):
    # Image with max side < 1200 px
    small_img = np.ones((400, 500), dtype=np.uint8) * 255
    img_path = tmp_path / "small.png"
    cv2.imwrite(str(img_path), small_img)

    with pytest.raises(IngestError) as exc_info:
        ingest(str(img_path), str(tmp_path / "out"))
    assert "IMAGE_TOO_SMALL" in str(exc_info.value)


def test_ingest_raster_valid(tmp_path):
    # Valid image >= 1200 px on long side
    valid_img = np.ones((1300, 1600), dtype=np.uint8) * 255
    # Draw simple orthogonal black lines
    cv2.line(valid_img, (200, 650), (1400, 650), 0, 3)
    cv2.line(valid_img, (800, 200), (800, 1100), 0, 3)

    img_path = tmp_path / "schematic.png"
    cv2.imwrite(str(img_path), valid_img)

    out_dir = tmp_path / "out"
    meta = ingest(str(img_path), str(out_dir))

    assert isinstance(meta, PageMeta)
    assert meta.mode == "raster"
    assert meta.width_px == 1600
    assert meta.height_px == 1300
    assert (out_dir / "page.png").exists()
    assert (out_dir / "page.meta.json").exists()


def test_ingest_vector_pdf_valid(tmp_path):
    import fitz

    # Create a synthetic 1-page vector PDF
    pdf_path = tmp_path / "synthetic_vector.pdf"
    doc = fitz.open()
    page = doc.new_page(width=800, height=600)

    # Insert text
    page.insert_text(fitz.Point(100, 100), "R1 10k")
    page.insert_text(fitz.Point(300, 100), "C1 100nF")

    # Draw more than min_vector_paths drawings
    for y in range(50, 400, 20):
        shape = page.new_shape()
        shape.draw_line(fitz.Point(50, y), fitz.Point(500, y))
        shape.finish(color=(0, 0, 0), width=2)
        shape.commit()

    doc.save(str(pdf_path))
    doc.close()

    out_dir = tmp_path / "out_pdf"
    meta = ingest(str(pdf_path), str(out_dir))

    assert isinstance(meta, PageMeta)
    assert meta.mode == "vector"
    assert meta.width_px >= 1200
    assert (out_dir / "page.png").exists()
    assert (out_dir / "page.meta.json").exists()


def test_ingest_rejects_multipage_pdf(tmp_path):
    import fitz

    # Create a 2-page PDF
    pdf_path = tmp_path / "multipage.pdf"
    doc = fitz.open()
    p1 = doc.new_page(width=800, height=600)
    p1.insert_text(fitz.Point(100, 100), "Page 1")
    p2 = doc.new_page(width=800, height=600)
    p2.insert_text(fitz.Point(100, 100), "Page 2")
    doc.save(str(pdf_path))
    doc.close()

    with pytest.raises(IngestError) as exc_info:
        ingest(str(pdf_path), str(tmp_path / "out_multi"))
    assert "MULTI_PAGE" in str(exc_info.value)
