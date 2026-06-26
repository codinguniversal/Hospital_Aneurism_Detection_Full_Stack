import asyncio

import pytest
from unittest.mock import AsyncMock
from app.core.patient_management.use_cases import ScanAnalysisUseCase
from app.core.patient_management.entities import AneurysmAnalysisResultEntity

# Import your test mock notifier
from tests.mocks.mock_notifier import MockNotificationService

@pytest.mark.asyncio
async def test_scan_analysis_triggers_notification_on_high_risk():
    # 1. Arrange Mocks
    mock_patient_repo = AsyncMock()
    mock_ai_service = AsyncMock()
    mock_settings_repo = AsyncMock()
    mock_notifier = MockNotificationService()

    # Configure mock repository to return a binary scan file stub
    mock_patient_repo.get_scan_file.return_value = b"fake_binary_dicom_data"

    # Configure mock settings repo to return our dynamic risk threshold (e.g., 0.70)
    mock_settings = AsyncMock()
    mock_settings.aneurysm_high_risk_threshold = 0.70
    mock_settings_repo.get_settings.return_value = mock_settings

    # Configure mock AI service to yield a high-risk result (0.85 probability)
    mock_result = AsyncMock()
    mock_result.overall.probability = 0.85
    mock_ai_service.analyze_scan.return_value = mock_result

    # 2. Inject components into the Use Case
    use_case = ScanAnalysisUseCase(
        patient_repo=mock_patient_repo,
        ai_service=mock_ai_service,
        notifier=mock_notifier,        #  Injected mock notifier
        settings_repo=mock_settings_repo
    )

    # 3. Act
    await use_case.execute(scan_id="scan_123_abc")

    await asyncio.sleep(0)
    # 4. Assert
    # Verify that exactly 1 alert was recorded in memory
    assert len(mock_notifier.sent_alerts) == 1
    assert mock_notifier.sent_alerts[0]["scan_id"] == "scan_123_abc"
    assert mock_notifier.sent_alerts[0]["probability"] == 0.85


@pytest.mark.asyncio
async def test_scan_analysis_skips_notification_on_low_risk():
    # 1. Arrange Mocks
    mock_patient_repo = AsyncMock()
    mock_ai_service = AsyncMock()
    mock_settings_repo = AsyncMock()
    mock_notifier = MockNotificationService()

    mock_patient_repo.get_scan_file.return_value = b"fake_binary_dicom_data"
    
    mock_settings = AsyncMock()
    mock_settings.aneurysm_high_risk_threshold = 0.70
    mock_settings_repo.get_settings.return_value = mock_settings

    # Configure mock AI to yield a safe, low-risk result (0.32 probability)
    mock_result = AsyncMock()
    mock_result.overall.probability = 0.32
    mock_ai_service.analyze_scan.return_value = mock_result

    use_case = ScanAnalysisUseCase(
        patient_repo=mock_patient_repo,
        ai_service=mock_ai_service,
        notifier=mock_notifier,
        settings_repo=mock_settings_repo
    )

    # 2. Act
    await use_case.execute(scan_id="scan_safe_456")

    # 3. Assert
    # Since 0.32 < 0.70 threshold, the sent_alerts log list should remain totally empty!
    assert len(mock_notifier.sent_alerts) == 0