import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.load_report import collect_specs

st.set_page_config(page_title="AI Test Copilot", layout="wide")
st.title("AI Test Copilot — Run Dashboard")

uploaded = st.file_uploader("Upload a Playwright JSON report", type="json")

if uploaded:
    report = json.load(uploaded)
    stats = report["stats"]

    total = stats["expected"] + stats["unexpected"] + stats["skipped"]
    passed = stats["expected"]
    failed = stats["unexpected"]
    rate = round(passed / total * 100, 1) if total > 0 else 0.0

    # --- Top metrics row ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("Passed", passed)
    c3.metric(
        "Failed", failed, delta=f"-{failed}" if failed else None, delta_color="inverse"
    )
    c4.metric("Pass rate", f"{rate}%")

    st.divider()

    # --- Failed tests ---
    specs = collect_specs(report["suites"])
    failed_specs = [s for s in specs if not s["ok"]]

    if failed_specs:
        st.subheader(f"Failed tests ({len(failed_specs)})")
        for s in failed_specs:
            st.error(f"**{s['file']}** — {s['title']}")
    else:
        st.success("All tests passed!")

    # --- Results by tag ---
    st.divider()
    st.subheader("Results by tag")
    tag_counts: dict[str, dict[str, int]] = {}
    for s in specs:
        for tag in s.get("tags", []):
            if tag not in tag_counts:
                tag_counts[tag] = {"passed": 0, "failed": 0}
            if s["ok"]:
                tag_counts[tag]["passed"] += 1
            else:
                tag_counts[tag]["failed"] += 1

    cols = st.columns(len(tag_counts))
    for col, (tag, counts) in zip(cols, sorted(tag_counts.items())):
        t = counts["passed"] + counts["failed"]
        col.metric(f"@{tag}", f"{counts['passed']}/{t}", delta_color="off")

# Streamlit up command: streamlit run src/dashboard.py
