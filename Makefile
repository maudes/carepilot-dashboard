.PHONY: help check-libs setup install dev api ui test lint clean reset-env docker-up docker-down

help:
	@echo "Targets:"
	@echo "  setup       Install dependencies (including dev tools) from uv.lock"
	@echo "  install     Install runtime dependencies only"
	@echo "  dev         Run the FastAPI backend and the Streamlit dashboard"
	@echo "  api / ui    Run only the backend / only the dashboard"
	@echo "  test        Run pytest"
	@echo "  lint        Format with black and isort"
	@echo "  clean       Remove caches"
	@echo "  reset-env   Recreate the virtual environment"
	@echo "  docker-up   Optional: run the backend in Docker"
	@echo "  docker-down Optional: stop the Docker services"

# WeasyPrint needs cairo and pango from the system
check-libs:
	@if [ "$$(uname)" = "Darwin" ]; then \
		for p in cairo pango; do \
			brew list $$p >/dev/null 2>&1 || { echo "Missing $$p. Run: brew install $$p"; exit 1; }; \
		done; \
	else \
		echo "Linux: make sure libcairo2, libpango-1.0-0 and libpangocairo-1.0-0 are installed"; \
	fi

setup: check-libs
	uv sync --frozen --extra dev

install: check-libs
	uv sync --frozen --no-dev

api:
	uv run uvicorn backend.main:app --reload

ui:
	uv run streamlit run dashboard/app.py

# Start the backend in the background, and stop it when the dashboard exits
dev:
	@uv run uvicorn backend.main:app --reload & pid=$$!; \
	trap 'kill $$pid 2>/dev/null' EXIT INT TERM; \
	sleep 2; \
	uv run streamlit run dashboard/app.py

test:
	uv run pytest

lint:
	uv run black .
	uv run isort .

clean:
	rm -rf .pytest_cache
	find . -name "__pycache__" -not -path "./.venv/*" -prune -exec rm -rf {} +

reset-env:
	rm -rf .venv
	uv sync --frozen --extra dev

# Optional: Docker is not required to run HealthTally
docker-up:
	docker compose --profile development up --build

docker-down:
	docker compose --profile development down
