import pytest
from unittest.mock import patch, AsyncMock

from app.infrastructure.scheduler.scheduler import run_timeframe_scan_analysis, start_apscheduler
from app.modules.system_settings.entities import SettingsEntity

class DummyScan:
    def __init__(self, scan_id):
        self.id = scan_id

@pytest.mark.asyncio
async def test_run_timeframe_scan_analysis_success():
    """Test that the scheduler fetches pending scans and processes them successfully."""
    mock_settings_repo = AsyncMock()
    mock_settings_repo.get_settings.return_value = SettingsEntity(
        ai_api_url="http://localhost",
        ai_timeout_limit=30,
        automatic_scan_start_hour=1,
        automatic_scan_end_hour=5,
        automatic_scan_interval=60,
        aneurysm_high_risk_threshold=0.8,
        aneurysm_medium_risk_threshold=0.5
    )

    mock_patient_repo = AsyncMock()
    mock_patient_repo.get_all_pending_scans.return_value = [DummyScan("scan_1"), DummyScan("scan_2")]

    mock_scan_analysis = AsyncMock()
    
    with patch("app.infrastructure.scheduler.scheduler.build_settings_repository", return_value=mock_settings_repo), \
         patch("app.infrastructure.scheduler.scheduler.build_patient_repository", return_value=mock_patient_repo), \
         patch("app.infrastructure.scheduler.scheduler.build_scan_analysis_use_case", return_value=mock_scan_analysis):
         
         await run_timeframe_scan_analysis()
         
         mock_patient_repo.get_all_pending_scans.assert_called_once()
         assert mock_scan_analysis.execute.call_count == 2
         mock_scan_analysis.execute.assert_any_call(scan_id="scan_1")
         mock_scan_analysis.execute.assert_any_call(scan_id="scan_2")

@pytest.mark.asyncio
async def test_run_timeframe_scan_analysis_repo_error(caplog):
    """Test that a repository error does not crash the scheduler."""
    mock_settings_repo = AsyncMock()
    mock_patient_repo = AsyncMock()
    mock_patient_repo.get_all_pending_scans.side_effect = Exception("DB Error")
    mock_scan_analysis = AsyncMock()

    with patch("app.infrastructure.scheduler.scheduler.build_settings_repository", return_value=mock_settings_repo), \
         patch("app.infrastructure.scheduler.scheduler.build_patient_repository", return_value=mock_patient_repo), \
         patch("app.infrastructure.scheduler.scheduler.build_scan_analysis_use_case", return_value=mock_scan_analysis):
         
         await run_timeframe_scan_analysis()
         
         # The use case should not be called if repo fails
         mock_scan_analysis.execute.assert_not_called()
         assert "Failed to fetch pending scans from repository: DB Error" in caplog.text

@pytest.mark.asyncio
async def test_run_timeframe_scan_analysis_use_case_error(caplog):
    """Test that an error processing one scan doesn't stop the processing of other scans."""
    mock_settings_repo = AsyncMock()
    mock_patient_repo = AsyncMock()
    mock_patient_repo.get_all_pending_scans.return_value = [DummyScan("scan_1"), DummyScan("scan_2")]

    mock_scan_analysis = AsyncMock()
    # Raise exception on first call, succeed on second
    mock_scan_analysis.execute.side_effect = [Exception("Analysis Error"), None]

    with patch("app.infrastructure.scheduler.scheduler.build_settings_repository", return_value=mock_settings_repo), \
         patch("app.infrastructure.scheduler.scheduler.build_patient_repository", return_value=mock_patient_repo), \
         patch("app.infrastructure.scheduler.scheduler.build_scan_analysis_use_case", return_value=mock_scan_analysis):
         
         await run_timeframe_scan_analysis()
         
         # Both should be called despite the first one raising an error
         assert mock_scan_analysis.execute.call_count == 2
         assert "Failed processing automatic scan scan_1: Analysis Error" in caplog.text

@pytest.mark.asyncio
@patch("app.infrastructure.scheduler.scheduler.scheduler")
async def test_start_apscheduler(mock_scheduler):
    """Test that start_apscheduler correctly registers the cron job."""
    mock_settings_repo = AsyncMock()
    mock_settings_repo.get_settings.return_value = SettingsEntity(
        ai_api_url="http://localhost",
        ai_timeout_limit=30,
        automatic_scan_start_hour=1,
        automatic_scan_end_hour=5,
        automatic_scan_interval=60,
        aneurysm_high_risk_threshold=0.8,
        aneurysm_medium_risk_threshold=0.5
    )
    
    with patch("app.infrastructure.scheduler.scheduler.build_settings_repository", return_value=mock_settings_repo):
        await start_apscheduler()
        
        mock_scheduler.add_job.assert_called_once_with(
            run_timeframe_scan_analysis,
            trigger="cron",
            hour="1-5",
            minute="0",
            id="aneurysm_idle_batch_job"
        )
        mock_scheduler.start.assert_called_once()
