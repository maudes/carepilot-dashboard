# CarePilot

CarePilot is a personal project designed to help users record and track their health data over time. It provides features for inputting personal metrics, setting health goals, visualizing long-term trends, and exporting data files. Beyond its practical use, CarePilot also serves as a technical playground for experimenting with:

- Frontend-backend separation
- Automated database deployment via CI/CD
- Multi-environment testing
- Third-party API integration
- FHIR data structure transformation

---

## Project Planning

| Phase | Description |
|-------|-------------|
| **Phase 1** | Structure setup and implementation of core features |
| **Phase 2** | FHIR conversion and third-party API integration |
| **Phase 3** | Expansion to support pet health tracking |

---

## Project Structure

This repository follows a modular structure to support scalability and maintainability:

```
carepilot-dashboard/
├── backend/                      # FastAPI backend
│   ├── alembic/                  # Alembic migration scripts
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── README.md
│   │   ├── script.py.mako
│   ├── config/                   # Configuration settings
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models/                   # ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── umixin.py
│   ├── routers/                  # API route definitions
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── dailylog.py
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── goal.py
│   │   └── vitalsign.py
│   ├── services/                 # Business logic
│   ├── __init__.py
│   ├── alembic.ini
│   ├── db.py                     # DB session and engine setup
│   └── main.py                   # FastAPI entry point
├── dashboard/                    # Frontend dashboard (TBD)
├── tests/                        # Backend test cases
├── .gitignore                    # Git ignore rules
├── LICENSE                       # MIT License
├── Makefile                      # Task automation
├── README.md                     # Project documentation
├── docker-compose.yml            # Docker orchestration
├── pyproject.toml                # Python project configuration
├── pytest.ini                    # Pytest configuration
└── uv.lock                       # Dependency lock file

```

---

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, Pydantic, Redis
- **Database**: PostgreSQL with Alembic for migrations
- **DevOps**: Docker, CI/CD pipelines, multi-env setup
- **Standards**: FHIR (HL7) for health data interoperability
- **Testing**: Pytest

---


