import sys

import pandas as pd


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m src.analyse <results.csv>")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1])

    print(f"=== Loaded {len(df)} test results ===\n")

    # --- Pass rate by file ---
    by_file = (
        df.groupby("file")["ok"]
        .agg(total="count", passed="sum")
        .assign(pass_rate=lambda x: (x["passed"] / x["total"] * 100).round(1))
        .sort_values("pass_rate")
    )
    print("Pass rate by file:")
    print(by_file.to_string())
    print()

    # --- Pass rate by tag ---
    tag_rows = []
    for _, row in df.iterrows():
        for tag in str(row["tags"]).split("|"):
            if tag and tag != "nan":
                tag_rows.append({"tag": tag, "ok": row["ok"]})

    tag_df = pd.DataFrame(tag_rows)
    by_tag = (
        tag_df.groupby("tag")["ok"]
        .agg(total="count", passed="sum")
        .assign(pass_rate=lambda x: (x["passed"] / x["total"] * 100).round(1))
        .sort_values("pass_rate")
    )
    print("Pass rate by tag:")
    print(by_tag.to_string())
    print()

    # --- Slowest 5 tests ---
    print("Slowest 5 tests:")
    slowest = df.nlargest(5, "duration_ms")[["title", "duration_ms", "ok"]]
    print(slowest.to_string(index=False))


if __name__ == "__main__":
    main()
