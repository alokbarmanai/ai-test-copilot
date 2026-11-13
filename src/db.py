import json
import sqlite3
from pathlib import Path
from src.load_report import collect_specs

DB_PATH = Path("data/results.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id        TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                total     INTEGER NOT NULL,
                passed    INTEGER NOT NULL,
                failed    INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS results (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id    TEXT NOT NULL REFERENCES runs(id),
                file      TEXT NOT NULL,
                title     TEXT NOT NULL,
                ok        INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                tags      TEXT NOT NULL
            );
        """)


def import_report(report: dict, run_id: str) -> int:
    """Import a Playwright JSON report into the database. Returns spec count."""
    stats = report["stats"]
    total = stats["expected"] + stats["unexpected"] + stats["skipped"]

    specs = collect_specs(report["suites"])

    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?)",
            (
                run_id,
                stats["startTime"],
                stats["duration"],
                total,
                stats["expected"],
                stats["unexpected"],
            ),
        )
        conn.executemany(
            "INSERT INTO results (run_id, file, title, ok, duration_ms, tags) VALUES (?,?,?,?,?,?)",
            [
                (
                    run_id,
                    s.get("file", ""),
                    s["title"],
                    int(s["ok"]),
                    (
                        s.get("tests", [{}])[0]
                        .get("results", [{}])[0]
                        .get("duration", 0)
                        if s.get("tests") and s["tests"][0].get("results")
                        else 0
                    ),
                    "|".join(s.get("tags", [])),
                )
                for s in specs
            ],
        )
    return len(specs)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m src.db <report.json> <run-id>")
        sys.exit(1)

    init_db()
    with open(sys.argv[1], encoding="utf-8-sig") as f:
        report = json.load(f)

    count = import_report(report, run_id=sys.argv[2])
    print(f"Imported {count} specs as run '{sys.argv[2]}'")
