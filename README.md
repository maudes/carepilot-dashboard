# CarePilot

CarePilot is a personal project for recording and tracking health data over time. It offers features such as metric input, goal setting, trend visualization, and data export. Beyond its practical use, it serves as a technical sandbox for exploring backend architecture, authentication, and health data standards.

### Key Features

- Health data input, record review, goal setting, trend visualization, and export
- Frontend-backend separation with Streamlit + FastAPI
- JWT & OTP authentication, multi-environment setup
- SQLAlchemy ORM with Pydantic schema, Alembic migrations
- Unit testing via pytest

### Tech Stack

| Category     | Technologies Used                                      |
|--------------|--------------------------------------------------------|
| **Backend**  | FastAPI, SQLAlchemy, Pydantic, Redis, SMTP             |
| **Database** | PostgreSQL + Alembic                                   |
| **DevOps**   | Docker, multi-env configuration                        |
| **Standards**| FHIR (HL7) for health data interoperability            |
| **Testing**  | Pytest                                                 |


---

## Project Planning

| Phase | Description |
|-------|-------------|
| **Phase 1** (Done, Aug 2025)| Core feature implementation: CRUD, authentication, and architecture setup|
| **Phase 2** (WIP)| FHIR conversion, MQTT, export and third-party API integration |
| **Phase 3** (Planned)| Extend support for pet health tracking |

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
├── dashboard/                    # Frontend dashboard
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


---




