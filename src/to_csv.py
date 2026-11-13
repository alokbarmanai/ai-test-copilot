import csv
import json
import sys
from pathlib import Path
from src.load_report import collect_specs


def report_to_rows(report: dict, run_id: str) -> list[dict]:
    """Flatten a Playwright report into one row per spec."""
    specs = collect_specs(report["suites"])
    rows = []
    for s in specs:
        results = s.get("tests", [{}])[0].get("results", [{}])
        duration = results[0].get("duration", 0) if results else 0
        rows.append(
            {
                "run_id": run_id,
                "file": s.get("file", ""),
                "title": s["title"],
                "ok": s["ok"],
                "duration_ms": duration,
                "tags": "|".join(s.get("tags", [])),
            }
        )
    return rows


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python src/to_csv.py <report.json> <output.csv>")
        sys.exit(1)

    report_path, out_path = sys.argv[1], sys.argv[2]
    with open(report_path, encoding="utf-8-sig") as f:
        report = json.load(f)

    rows = report_to_rows(report, run_id="run-001")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Written {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
