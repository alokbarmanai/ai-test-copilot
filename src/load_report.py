import json
from pathlib import Path


def load_report(path: str) -> dict:
    """Load a Playwright JSON report from disk and return it as a dict."""
    with open(Path(path), encoding="utf-8-sig") as f:
        return json.load(f)


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

    if failed > 0:
        print("Failed suites:")
        for suite in report["suites"]:
            failed_specs = [s for s in suite["specs"] if not s["ok"]]
            if failed_specs:
                print(f"  {suite['title']}")
                for spec in failed_specs:
                    print(f"    ✗ {spec['title']}")
    else:
        print("All tests passed.")


def main() -> None:
    report = load_report(
        r"D:\Development Projects\source\ai projects\shopease\shopease-tests-report.json"
    )
    print_summary(report)


if __name__ == "__main__":
    main()
