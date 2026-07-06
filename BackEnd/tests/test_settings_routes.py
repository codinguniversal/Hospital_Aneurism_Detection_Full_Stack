"""
Tests for admin settings route: PUT /admin/settings
"""
import pytest
from fastapi import status


class TestAdminSettingsRoute:
    """Tests for PUT /admin/settings endpoint."""

    @pytest.fixture(autouse=True)
    def override_claims_as_admin(self):
        from app.api.v1.dependencies.auth import get_current_user_claims
        from app.main import app
        app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "admin@test.com", "role": "Admin", "employee_id": "EMP-99999"}
        yield
        # conftest's teardown will clear dependency_overrides, so no explicit cleanup is strictly needed, but let's yield anyway.

    def test_update_settings_success(self, client, stub_update_settings):
        """Should return 200 with updated settings on valid payload."""
        payload = {
            "ai_api_url": "http://localhost:5000/predict",
            "ai_timeout_limit": 20,
            "automatic_scan_start_hour": 1,
            "automatic_scan_end_hour": 5,
            "automatic_scan_interval": 60,
            "aneurysm_high_risk_threshold": 0.85,
            "aneurysm_medium_risk_threshold": 0.5
        }

        response = client.put("/admin/settings", json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["ai_api_url"] == payload["ai_api_url"]
        assert response.json()["aneurysm_high_risk_threshold"] == payload["aneurysm_high_risk_threshold"]
        assert response.json()["aneurysm_medium_risk_threshold"] == payload["aneurysm_medium_risk_threshold"]

    def test_update_settings_invalid_time_range(self, client, stub_update_settings):
        """Should return 400 when start_hour >= end_hour."""
        payload = {
            "ai_api_url": "http://localhost:5000/predict",
            "ai_timeout_limit": 20,
            "automatic_scan_start_hour": 5,
            "automatic_scan_end_hour": 4,  # Invalid: start > end
            "automatic_scan_interval": 60,
            "aneurysm_high_risk_threshold": 0.8,
            "aneurysm_medium_risk_threshold": 0.5
        }

        response = client.put("/admin/settings", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Start hour must be less than end hour" in response.json()["detail"]

    def test_update_settings_invalid_thresholds(self, client, stub_update_settings):
        """Should return 400 when high_risk_threshold <= medium_risk_threshold."""
        payload = {
            "ai_api_url": "http://localhost:5000/predict",
            "ai_timeout_limit": 20,
            "automatic_scan_start_hour": 1,
            "automatic_scan_end_hour": 5,
            "automatic_scan_interval": 60,
            "aneurysm_high_risk_threshold": 0.4,  # Invalid: lower than medium
            "aneurysm_medium_risk_threshold": 0.5
        }

        response = client.put("/admin/settings", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "High risk threshold must be greater than medium risk threshold" in response.json()["detail"]

    def test_update_settings_stores_values(self, client, stub_update_settings):
        """Should store updated values in the stub for verification."""
        payload = {
            "ai_api_url": "http://newapi:9000/analyze",
            "ai_timeout_limit": 45,
            "automatic_scan_start_hour": 2,
            "automatic_scan_end_hour": 6,
            "automatic_scan_interval": 90,
            "aneurysm_high_risk_threshold": 0.9,
            "aneurysm_medium_risk_threshold": 0.6
        }

        response = client.put("/admin/settings", json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert stub_update_settings.updated_settings is not None
        assert stub_update_settings.updated_settings.ai_timeout_limit == 45
