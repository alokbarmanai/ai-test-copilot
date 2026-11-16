# AI Test Copilot

A Python service that ingests Playwright test reports, stores results in SQLite, and surfaces quality insights — the data layer for an AI-powered QA assistant.

**Stack:** Python 3.12 · FastAPI · SQLite · pandas · Streamlit · Docker · GitHub Actions

---

## Quick start

```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements-dev.txt
uvicorn src.api:app --reload
# Open http://localhost:8000/docs