import os

# Base URL of the HealthTally API. Override it when the backend runs elsewhere,
# for example API_URL=http://web:8000 inside docker compose.
API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
