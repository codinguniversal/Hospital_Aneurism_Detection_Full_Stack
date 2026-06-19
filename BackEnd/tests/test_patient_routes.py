from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_patient_records_use_case
from app.domain.entities import PatientEntity, ScanEntity, ScanStatus

client = TestClient(app)

class StubGetPatientRecordsUseCase:
    def __init__(self):
        self.mock_patients = []

    async def execute(self):
        return self.mock_patients

stub_use_case = StubGetPatientRecordsUseCase()

@pytest.fixture(autouse=True)
def setup_use_case_override():
    app.dependency_overrides[get_patient_records_use_case] = lambda: stub_use_case
    yield
    app.dependency_overrides.clear()


class TestPatientRoutes:

    def test_get_records_success(self):
        # Arrange: Give Alice a mock Scan object so patient.scans[0] is happy
        mock_scan = ScanEntity(
            id="scan_001",
            scan_date=datetime.now(),
            img_file_path="/data/scans/scan_001.dcm",
            status=ScanStatus.COMPLETED,  # Use the enum for clarity
            results=None  # Our entities handle empty results gracefully now!
        )
        
        stub_use_case.mock_patients = [
            PatientEntity(
                id="pat_001",
                patient_name="Alice Smith",
                birth_date=datetime(1990, 5, 20),
                assigned_doc="Dr. Johnson",
                scans=[mock_scan])
        ]
        
        # Act
        response = client.get("/patients/records")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Smith"

    def test_get_records_empty_state(self):
        # Arrange: Clear data to trigger your route's 404 guard clause
        stub_use_case.mock_patients = []
        
        # Act
        response = client.get("/patients/records")
        
        # Assert: Expect a 404 as defined by your application's business rules!
        assert response.status_code == 404
        assert response.json()["detail"] == "No Patient Records  were  found"