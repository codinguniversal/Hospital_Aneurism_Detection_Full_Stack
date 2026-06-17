from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from datetime import datetime
from app.config import settings
from app.services.data_layer import get_data_layer
from app.services.ai_service import get_ai_service
from BackEnd.app.usecases.scan_analysis_use_case import ScanAnalysisUseCase 

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def run_timeframe_scan_analysis():
    """called when within the timeframe"""
    data_layer = get_data_layer()
    ai_service = get_ai_service()
    use_case = ScanAnalysisUseCase(data_layer= data_layer, ai_service= ai_service)

    pending_scans = await data_layer.get_all_pending_scans()

    for scan in pending_scans:
        scan_id = scan.get("id")
        if not scan_id or not isinstance(scan_id, str):
            logger.warning("Encountered pending scan with a missing or invalid ID format.")
            continue
        try:
            await use_case.execute(scan_id= scan_id)
        except Exception as exc:
            logger.error(f"Failed processing automatic scan {scan_id}: {exc}")
            continue
def start_apscheduler():
    """defines the time frame for the scan execution
    using cron rules: minute hour dayOfTheMonth month dayOfTheWeek
    """

    scheduler.add_job(
        run_timeframe_scan_analysis,
        trigger = "cron",
        hour = f"{settings.automatic_scan_start_hour}-{settings.automatic_scan_end_hour}",
        minute = "0",
        id = "aneurysm_idle_batch_job"
    )
    scheduler.start()
