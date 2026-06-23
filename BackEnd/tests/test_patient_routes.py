from datetime import datetime, date
import pytest
from fastapi import status
from app.core.patient_management.entities import PatientEntity, ScanEntity, ScanStatus


class TestPatientRecordsRoute:
    """Tests for GET /patients/records endpoint."""

    def test_get_records_success(self, client, stub_records):
        """Should return 200 with list of patient records when data exists."""
        # Arrange
        stub_records.mock_patients = [
            PatientEntity(
                id="pat_001",
                patient_name="Alice Smith",
                birth_date=date(1985, 4, 12),
                assigned_doc="dr_smith",
                medical_history=["Hypertension"],
                scans=[
                    ScanEntity(
                        id="SCN-1001",
                        scan_date=datetime.now(),
                        status=ScanStatus.COMPLETED,
                        img_file_path="E:/for database/Have Ane/1.zip",
                        results=None
                    )
                ]
            )
        ]
        
        # Act
        response = client.get("/patients/records")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Smith"
        assert data[0]["analyzed"] is True

    def test_get_records_empty_state(self, client, stub_records):
        """Should return 404 when no patient records exist."""
        # Arrange
        stub_records.mock_patients = []
        
        # Act
        response = client.get("/patients/records")
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPatientResultsRoute:
    """Tests for GET /patients/{patient_id} endpoint."""

    def test_get_patient_results_success(self, client, stub_results):
        """Should return 200 with patient details including scans."""
        # Arrange
        mock_scan = ScanEntity(
            id="SCN-2026-e6905722",
            scan_date=datetime(2026, 6, 18, 16, 32, 37),
            status=ScanStatus.COMPLETED,
            img_file_path="E:/for database/Have Ane/1.zip",
            results=None
        )

        stub_results.mock_patient = PatientEntity(
            id="PT-66457",
            patient_name="Brandi Gallagher",
            birth_date=date(1959, 8, 25),
            assigned_doc="dr_smith",
            medical_history=["Essential Hypertension."],
            scans=[mock_scan]
        )

        # Act
        response = client.get("/patients/PT-66457")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "PT-66457"
        assert data["patient_name"] == "Brandi Gallagher"
        assert len(data["scans"]) == 1
        assert data["scans"][0]["status"] == "completed"

    def test_get_patient_results_not_found(self, client, stub_results):
        """Should return 404 when patient ID doesn't exist."""
        # Arrange
        stub_results.mock_patient = None

        # Act
        response = client.get("/patients/PT-NONEXISTENT")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "The Patient was not found"
