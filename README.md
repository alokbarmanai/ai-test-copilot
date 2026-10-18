# AI Test Copilot

An AI assistant for QA teams: it searches requirements, API specifications, test cases and
automation logs, and generates **traceable test scenarios and test plans** – with evaluation,
guardrails and CI quality gates.

> Status: **in development** – learning project following an AI Quality Engineer roadmap.
> First knowledge base: the [ShopEase](https://github.com/alokbarmanai/shopease) demo project.

## Tech Stack
Python · FastAPI · pytest · LLM API · vector database · LangGraph · Docker · GitHub Actions

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell)
python -m pip install -r requirements-dev.txt
```

## Development Commands

| Command | Purpose |
|---------|---------|
| `python hello.py` | Smoke check of the environment |
| `ruff check .` | Lint |
| `ruff format .` | Format |