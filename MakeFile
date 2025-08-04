.PHONY: dev test lint clean reset-env

dev:
    uv run uvicorn backend.main:app --reload &
    sleep 2
    uv run streamlit run dashboard/app.py
    
test:
    uv run pytest

lint:
    uv run black .
    uv run isort .

clean:
    rm -rf .venv __pycache__ .pytest_cache *.pyc *.log

reset-env:
    rm -rf .venv
    uv venv .venv
    uv sync --no-dev
