"""
tests/test_pipeline.py  --  Tests for the complete end-to-end pipeline runner (core/pipeline.py).
"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import DesignIR
from core.pipeline import run_pipeline
from vision.ingest import IngestError


def test_pipeline_reject_nonexistent():
    with pytest.raises((FileNotFoundError, IngestError)):
        run_pipeline("non_existent_file.pdf", "out/test_nonexistent")


def test_pipeline_reject_unsupported_extension(tmp_path):
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("not a schematic")
    out_dir = tmp_path / "out"
    with pytest.raises(IngestError) as exc_info:
        run_pipeline(str(bad_file), str(out_dir))
    assert "UNSUPPORTED_TYPE" in str(exc_info.value)
