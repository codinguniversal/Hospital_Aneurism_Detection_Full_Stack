"""
Shared test configuration and fixtures.
All stub use cases and dependency overrides are centralized here.
"""
import pytest
from fastapi import status
from app.config import static_settings
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import (
    get_patient_records_use_case,
    get_patient_results_use_case,
    get_authenticate_user_use_case,
    get_register_user_use_case,
    get_check_email_use_case,
    get_update_settings_use_case,
    get_scan_analysis_use_case,
    get_settings_use_case,
    initialize_infrastructure
)
from app.modules.identity_access.entities import UserEntity
from app.modules.system_settings.entities import SettingsEntity

# ============================================================================
# SHARED TEST CLIENT
# ============================================================================
@pytest.fixture(scope="session", autouse=True)
def setup_mock_infrastructure():
    """Set the database to mock mode and initialize the factory once for all tests."""
    static_settings.database_mode = "mock"
    initialize_infrastructure(None)  # No DB connection needed
    yield

@pytest.fixture
def client():
    """FastAPI test client for all routes."""
    return TestClient(app)


# ============================================================================
# STUB REPOSITORIES & USE CASES
# ============================================================================

class StubSettingsRepository:
    def __init__(self):
        self.settings = SettingsEntity(
            ai_api_url="http://localhost:5000/predict",
            ai_timeout_limit=30,
            automatic_scan_start_hour=1,
            automatic_scan_end_hour=5,
            automatic_scan_interval=60,
            aneurysm_high_risk_threshold=0.8,
            aneurysm_medium_risk_threshold=0.5
        )

    async def get_settings(self):
        return self.settings


class StubGetPatientRecordsUseCase:
    def __init__(self):
        self.mock_patients = []

    async def execute(self):
        return self.mock_patients


class StubGetPatientResultsUseCase:
    def __init__(self):
        self.mock_patient = None

    async def execute(self, patient_id: str):
        if self.mock_patient and self.mock_patient.id == patient_id:
            return self.mock_patient
        return None


class StubAuthenticateUserUseCase:
    def __init__(self):
        self.user = None

    async def execute(self, identifier: str, password: str):
        if not self.user:
            return None
        if self.user.password != password:
            return None
        if self.user.email == identifier or self.user.employee_id == identifier:
            return self.user
        return None


class StubRegisterUserUseCase:
    def __init__(self):
        self.users = []

    async def execute(self, email: str, password: str):
        if any(user.email == email for user in self.users):
            raise ValueError(f"A user with email '{email}' already exists.")

        new_user = UserEntity(
            employee_id="EMP-12345",
            email=email,
            password=password,
            role="Radiologist"
        )
        self.users.append(new_user)
        return new_user


class StubCheckEmailUseCase:
    def __init__(self):
        self.exists = False

    async def execute(self, email: str):
        return self.exists


class StubUpdateSettingsUseCase:
    def __init__(self):
        self.updated_settings = None

    async def execute(self, new_settings: SettingsEntity):
        self.updated_settings = new_settings
        return None


class StubScanAnalysisUseCase:
    def __init__(self):
        self.result = None
        self.raise_not_found = False

    async def execute(self, scan_id: str):
        if self.raise_not_found:
            raise ValueError(f"Scan record with id {scan_id} not found in DB")
        return self.result


# ============================================================================
# STUB FIXTURES
# ============================================================================

@pytest.fixture
def stub_records():
    """Fixture for StubGetPatientRecordsUseCase."""
    return StubGetPatientRecordsUseCase()


@pytest.fixture
def stub_results():
    """Fixture for StubGetPatientResultsUseCase."""
    return StubGetPatientResultsUseCase()


@pytest.fixture
def stub_auth():
    """Fixture for StubAuthenticateUserUseCase."""
    return StubAuthenticateUserUseCase()


@pytest.fixture
def stub_register():
    """Fixture for StubRegisterUserUseCase."""
    return StubRegisterUserUseCase()


@pytest.fixture
def stub_check_email():
    """Fixture for StubCheckEmailUseCase."""
    return StubCheckEmailUseCase()


@pytest.fixture
def stub_update_settings():
    """Fixture for StubUpdateSettingsUseCase."""
    return StubUpdateSettingsUseCase()


@pytest.fixture
def stub_scan_analysis():
    """Fixture for StubScanAnalysisUseCase."""
    return StubScanAnalysisUseCase()


# ============================================================================
# SHARED FIXTURE: Dependency Override Setup
# ============================================================================

@pytest.fixture(autouse=True)
def setup_use_case_overrides(stub_records, stub_results, stub_auth, stub_register, 
                             stub_check_email, stub_update_settings, stub_scan_analysis):
    """
    Auto-used fixture that sets up all dependency overrides before each test.
    Cleans up after the test completes.
    """
    app.dependency_overrides[get_patient_records_use_case] = lambda: stub_records
    app.dependency_overrides[get_patient_results_use_case] = lambda: stub_results
    app.dependency_overrides[get_authenticate_user_use_case] = lambda: stub_auth
    app.dependency_overrides[get_register_user_use_case] = lambda: stub_register
    app.dependency_overrides[get_check_email_use_case] = lambda: stub_check_email
    app.dependency_overrides[get_update_settings_use_case] = lambda: stub_update_settings
    app.dependency_overrides[get_scan_analysis_use_case] = lambda: stub_scan_analysis
    
    yield  # Run test
    
    app.dependency_overrides.clear()  # Clean up after
