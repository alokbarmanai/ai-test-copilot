from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)

MINIMAL_REPORT = {
    "config": {},
    "suites": [],
    "errors": [],
    "stats": {
        "startTime": "2026-01-01T00:00:00Z",
        "duration": 5000,
        "expected": 8,
        "skipped": 1,
        "unexpected": 1,
        "flaky": 0,
    },
}


# --- /health ---


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- /results ---


def test_upload_valid_report():
    r = client.post("/results", json=MINIMAL_REPORT)
    assert r.status_code == 200
    assert r.json()["message"] == "Report stored"


def test_upload_missing_required_keys():
    r = client.post("/results", json={"config": {}})
    assert r.status_code == 422


def test_upload_malformed_json():
    r = client.post(
        "/results",
        content=b"not json",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 422


def test_upload_too_large():
    r = client.post(
        "/results",
        content=b"{}",
        headers={
            "Content-Type": "application/json",
            "content-length": str(11 * 1024 * 1024),  # fake 11MB
        },
    )
    assert r.status_code == 413


# --- /summary ---


def test_summary_after_upload():
    client.post("/results", json=MINIMAL_REPORT)
    r = client.get("/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 10
    assert data["passed"] == 8
    assert data["failed"] == 1
    assert data["pass_rate"] == 80.0


def test_summary_no_report(monkeypatch):
    monkeypatch.setattr("src.api._report", None)
    r = client.get("/summary")
    assert r.status_code == 404
