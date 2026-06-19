from datetime import datetime, date
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_patient_records_use_case, get_patient_results_use_case
from app.domain.entities import PatientEntity, ScanEntity, ScanStatus

client = TestClient(app)

# --- STUBS FOR DEPENDENCIES ---

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


stub_records_use_case = StubGetPatientRecordsUseCase()
stub_results_use_case = StubGetPatientResultsUseCase()


@pytest.fixture(autouse=True)
def setup_use_case_overrides():
    # Bind stubs to their respective dependency injection containers
    app.dependency_overrides[get_patient_records_use_case] = lambda: stub_records_use_case
    app.dependency_overrides[get_patient_results_use_case] = lambda: stub_results_use_case
    yield
    app.dependency_overrides.clear()


class TestPatientRoutes:

    # ==========================================
    # TESTS FOR: GET /patients/records
    # ==========================================

    def test_get_records_success(self):
        # Arrange
        mock_scan = ScanEntity(
            id="scan_001",
            scan_date=datetime.now(),
            img_file_path="/data/scans/scan_001.dcm",
            status=ScanStatus.COMPLETED,
            results=None
        )
        
        stub_records_use_case.mock_patients = [
            PatientEntity(
                id="pat_001",
                patient_name="Alice Smith",
                birth_date=date(1990, 5, 20),
                assigned_doc="Dr. Johnson",
                scans=[mock_scan]
            )
        ]
        
        # Act - Query cleanly without the /api layer
        response = client.get("/patients/records")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Smith"

    def test_get_records_empty_state(self):
        # Arrange
        stub_records_use_case.mock_patients = []
        
        # Act
        response = client.get("/patients/records")
        
        # Assert
        assert response.status_code == 404

    # ==========================================
    # TESTS FOR: GET /patients/{patient_id}
    # ==========================================

    def test_get_patient_results_success(self):
        # Arrange
        mock_scan = ScanEntity(
            id="SCN-2026-e6905722",
            scan_date=datetime(2026, 6, 18, 16, 32, 37),
            status=ScanStatus.COMPLETED,
            img_file_path="E:/for database/Have Ane/1.zip",
            results=None
        )

        stub_results_use_case.mock_patient = PatientEntity(
            id="PT-66457",
            patient_name="Brandi Gallagher",
            birth_date=date(1959, 8, 25),
            assigned_doc="dr_smith",
            medical_history=["Essential Hypertension."],
            scans=[mock_scan]
        )

        # Act - Query the singular patient route cleanly
        response = client.get("/patients/PT-66457")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "PT-66457"
        assert data["patient_name"] == "Brandi Gallagher"
        assert len(data["scans"]) == 1
        assert data["scans"][0]["status"] == "completed"

    def test_get_patient_results_not_found(self):
        # Arrange
        stub_results_use_case.mock_patient = None

        # Act
        response = client.get("/patients/PT-NONEXISTENT")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "The Patient was not found"