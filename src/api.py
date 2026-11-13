import logging
from fastapi import FastAPI, HTTPException, Query

from src.load_report import collect_specs, load_report
from src.db import get_connection, init_db

init_db()

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


@app.get("/db/summary")
def db_summary(file: str | None = Query(default=None)) -> list:
    """Query pass rate by file from SQLite. Optionally filter by file."""
    with get_connection() as conn:
        if file:
            rows = conn.execute(
                """
                SELECT file, COUNT(*) as total,
                       SUM(ok) as passed,
                       ROUND(AVG(ok) * 100, 1) as pass_rate
                FROM results WHERE file = ?
                GROUP BY file
                """,
                (file,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT file, COUNT(*) as total,
                       SUM(ok) as passed,
                       ROUND(AVG(ok) * 100, 1) as pass_rate
                FROM results
                GROUP BY file
                ORDER BY pass_rate
                """
            ).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No results found")
    return [dict(r) for r in rows]


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
