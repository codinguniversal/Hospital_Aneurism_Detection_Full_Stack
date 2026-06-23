"""
Tests for scan analysis route: POST /api/scans/{scan_id}/analyze
"""
import pytest
from fastapi import status
from app.core.patient_management.entities import (
    AneurysmAnalysisResultEntity,
    OverAllAneurysmPredictionEntity,
)


class TestScanAnalysisRoute:
    """Tests for POST /api/scans/{scan_id}/analyze endpoint."""

    def test_run_manual_analysis_success(self, client, stub_scan_analysis):
        """Should return 200 with analysis results on successful scan processing."""
        stub_scan_analysis.result = AneurysmAnalysisResultEntity(
            overall=OverAllAneurysmPredictionEntity(probability=0.92)
        )
        stub_scan_analysis.raise_not_found = False

        response = client.post(
            "/api/scans/SCN-1001/analyze",
            json={
                "patient_name": "Alice Smith",
                "scan_id": "SCN-1001"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["scan_id"] == "SCN-1001"
        assert data["patient_name"] == "Alice Smith"
        assert data["status"] == "completed"
        assert data["result"]["overall"]["probability"] == 0.92

    def test_run_manual_analysis_not_found(self, client, stub_scan_analysis):
        """Should return 404 when scan record doesn't exist."""
        stub_scan_analysis.raise_not_found = True

        response = client.post(
            "/api/scans/SCN-404/analyze",
            json={
                "patient_name": "Alice Smith",
                "scan_id": "SCN-404"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Scan record with id SCN-404 not found" in response.json()["detail"]

    def test_run_manual_analysis_with_different_scan_ids(self, client, stub_scan_analysis):
        """Should handle multiple scans with different IDs."""
        stub_scan_analysis.result = AneurysmAnalysisResultEntity(
            overall=OverAllAneurysmPredictionEntity(probability=0.65)
        )
        stub_scan_analysis.raise_not_found = False

        response = client.post(
            "/api/scans/SCN-5555/analyze",
            json={
                "patient_name": "John Doe",
                "scan_id": "SCN-5555"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["scan_id"] == "SCN-5555"
        assert data["patient_name"] == "John Doe"
        assert data["result"]["overall"]["probability"] == 0.65
