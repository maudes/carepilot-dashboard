FROM python:3.12-slim

# Runtime libraries for WeasyPrint. All Python dependencies ship wheels,
# so no compiler is needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Pinned uv, copied from the official image
COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /usr/local/bin/uv

# Keep the venv outside /app, so a bind mount over /app in docker-compose
# does not hide it
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install exactly what uv.lock says (runtime only, no dev tools)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

# Run as a non-root user
RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 8000

# Default command, can be overridden by docker-compose
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
