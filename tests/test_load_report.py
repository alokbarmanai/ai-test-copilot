import json
from pathlib import Path

import pytest

from src.load_report import collect_specs, load_report

# ---------------------------------------------------------------------------
# collect_specs
# ---------------------------------------------------------------------------


def test_collect_specs_flat():
    """Specs directly on a suite are returned."""
    suites = [{"specs": [{"title": "a"}, {"title": "b"}], "suites": []}]
    result = collect_specs(suites)
    assert len(result) == 2
    assert result[0]["title"] == "a"


def test_collect_specs_nested():
    """Specs in nested suites are also collected."""
    suites = [
        {
            "specs": [],
            "suites": [{"specs": [{"title": "nested"}], "suites": []}],
        }
    ]
    result = collect_specs(suites)
    assert len(result) == 1
    assert result[0]["title"] == "nested"


def test_collect_specs_empty():
    assert collect_specs([]) == []


# ---------------------------------------------------------------------------
# load_report
# ---------------------------------------------------------------------------


def test_load_report_missing_file():
    with pytest.raises(FileNotFoundError, match="Report not found"):
        load_report("does_not_exist.json")


def test_load_report_invalid_json(tmp_path: Path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_report(str(bad_file))


def test_load_report_valid(tmp_path: Path):
    data = {"config": {}, "suites": [], "errors": [], "stats": {}}
    report_file = tmp_path / "report.json"
    report_file.write_text(json.dumps(data), encoding="utf-8")
    result = load_report(str(report_file))
    assert result["suites"] == []
