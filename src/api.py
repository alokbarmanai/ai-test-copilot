import logging
from fastapi import FastAPI, HTTPException

from src.load_report import collect_specs, load_report

log = logging.getLogger(__name__)

app = FastAPI(title="AI Test Copilot", version="0.1.0")

# In-memory store — one report at a time for now
_report: dict | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/results")
def upload_results(payload: dict) -> dict:
    """Accept a Playwright JSON report and store it."""
    global _report
    required = {"config", "suites", "stats"}
    if not required.issubset(payload.keys()):
        raise HTTPException(
            status_code=422,
            detail=f"Missing required keys: {required - payload.keys()}",
        )
    _report = payload
    specs = collect_specs(_report["suites"])
    return {"message": "Report stored", "total_specs": len(specs)}


@app.get("/summary")
def get_summary() -> dict:
    """Return a quality summary of the stored report."""
    if _report is None:
        raise HTTPException(status_code=404, detail="No report loaded yet")

    stats = _report["stats"]
    total = stats["expected"] + stats["unexpected"] + stats["skipped"]
    passed = stats["expected"]
    failed = stats["unexpected"]

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 1) if total > 0 else 0.0,
        "duration_seconds": round(stats["duration"] / 1000, 1),
    }
