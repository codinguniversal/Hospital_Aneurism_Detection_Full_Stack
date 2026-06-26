==========================================================================
HOSPITAL ANEURYSM DETECTION SYSTEM - BACKEND ARCHITECTURE MAP
==========================================================================

[PROJECT ROOT] (D:\GIT Projects\Hospital_Aneurism_Detection_Full_Stack\backend)
 │
 ├── app/                             # Core Application Main Package
 │    ├── domain/                     # Entities, value objects, and repository interfaces
 │    ├── use_cases/                  # Interactors managing application rules (e.g., ScanAnalysis)
 │    ├── infrastructure/             # Concrete framework implementations & system adapters
 │    │    ├── common/                # Shared utilities (e.g., reflection.py dynamic loader)
 │    │    ├── notifications/         # Dynamic alert systems (Mailtrap HTTP API Providers)
 │    │    └── storage/               # Medical image persistence hooks (scan_slices/)
 │    ├── config.py                   # Pydantic Settings & Unified Environment management
 │    └── dependencies.py             # Dependency Injection Container & Reflection Factories
 │
 ├── tests/                           # Integration Testing & Route Validation Suite
 │    ├── test_auth_routes.py         # Verification scripts for user login & JWT security access
 │    ├── test_notification.py        # Pipeline tracking for clinical urgent alert triggers
 │    └── send_real_email.py          # Standalone dynamic integration script for Mailtrap sandbox
 │
 ├── .venv/                           # Isolated Project Virtual Environment Wrapper
 │    └── Lib/site-packages/          # Core framework binaries (FastAPI, Pydantic, Motor, PyJWT)
 │
 ├── postman/                         # API collection schema files for endpoint sanity checks
 ├── .gitignore                       # System filter file to prevent leaking local DB data / keys
 └── requirements.txt                 # The explicit configuration manifest for pip installs

==========================================================================
COMPONENT UTILITY INDEX
==========================================================================
Component Name         Primary Operational Responsibility
---------------------  ---------------------------------------------------
FastAPI / Uvicorn      High-performance asynchronous API routing & Gateway
Pydantic Settings      Silent environment variable injection & verification
Motor / PyMongo        Async Non-blocking drivers routing data to MongoDB
PyJWT / Bcrypt         Cryptographic security layer verifying hospital credentials
HTTPX AsyncClient      Fires background API payload delivery to remote servers
Pytest Core Engine     Isolated regression testing runner for endpoints
==========================================================================