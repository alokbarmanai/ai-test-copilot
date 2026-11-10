import json
import logging
import sys
from pathlib import Path

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


def load_report(path: str) -> dict:
    """Load a Playwright JSON report from disk and return it as a dict."""
    report_path = Path(path)
    if not report_path.exists():
        raise FileNotFoundError(f"Report not found: {report_path}")
    with open(report_path, encoding="utf-8-sig") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in report: {e}") from e


def collect_specs(suites: list) -> list[dict]:
    """Recursively collect all specs from nested suites."""
    specs = []
    for suite in suites:
        specs.extend(suite.get("specs", []))
        specs.extend(collect_specs(suite.get("suites", [])))
    return specs


def print_summary(report: dict) -> None:
    """Print a quality summary of a Playwright test run."""
    stats = report["stats"]
    total = stats["expected"] + stats["unexpected"] + stats["skipped"]
    passed = stats["expected"]
    failed = stats["unexpected"]
    skipped = stats["skipped"]
    duration = round(stats["duration"] / 1000, 1)
    pass_rate = round(passed / total * 100, 1) if total > 0 else 0.0

    print("=" * 50)
    print("ShopEase Test Run Summary")
    print("=" * 50)
    print(f"  Total tests : {total}")
    print(f"  Passed      : {passed}")
    print(f"  Failed      : {failed}")
    print(f"  Skipped     : {skipped}")
    print(f"  Pass rate   : {pass_rate}%")
    print(f"  Duration    : {duration}s")
    print()

    specs = collect_specs(report["suites"])

    # --- Failed tests ---
    failed_specs = [s for s in specs if not s["ok"]]
    if failed_specs:
        print("Failed tests:")
        for s in failed_specs:
            print(f"  ✗ [{s['file']}] {s['title']}")
        print()

    # --- Slowest tests (top 5) ---
    def spec_duration(s: dict) -> int:
        results = s.get("tests", [{}])[0].get("results", [{}])
        return results[0].get("duration", 0) if results else 0

    slowest = sorted(specs, key=spec_duration, reverse=True)[:5]
    print("Slowest tests (top 5):")
    for s in slowest:
        ms = spec_duration(s)
        print(f"  {ms:>6}ms  {s['title']}")
    print()

    # --- Results by tag ---
    tag_counts: dict[str, dict[str, int]] = {}
    for s in specs:
        for tag in s.get("tags", []):
            if tag not in tag_counts:
                tag_counts[tag] = {"passed": 0, "failed": 0}
            if s["ok"]:
                tag_counts[tag]["passed"] += 1
            else:
                tag_counts[tag]["failed"] += 1

    if tag_counts:
        print("Results by tag:")
        for tag, counts in sorted(tag_counts.items()):
            total_tag = counts["passed"] + counts["failed"]
            print(f"  @{tag:<10} {counts['passed']}/{total_tag} passed")


def main() -> None:
    if len(sys.argv) < 2:
        log.error("Usage: python load_report.py <path-to-report.json>")
        sys.exit(1)

    path = sys.argv[1]
    log.info("Loading report: %s", path)

    try:
        report = load_report(path)
    except (FileNotFoundError, ValueError) as e:
        log.error("%s", e)
        sys.exit(1)

    print_summary(report)


if __name__ == "__main__":
    main()

# run command: python src/load_report.py "D:\Development Projects\source\ai projects\shopease\shopease-tests-report.json"
