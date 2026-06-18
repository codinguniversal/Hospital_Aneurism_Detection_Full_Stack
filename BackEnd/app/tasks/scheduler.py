import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.dependencies import get_patient_repository, get_scan_analysis_use_case
from app.config import settings


logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def run_timeframe_scan_analysis():
    """called when within the timeframe"""
    patient_repo = get_patient_repository()
    scan_analysis_use_case = get_scan_analysis_use_case()

    try:
        pending_scans = await patient_repo.get_all_pending_scans()
    except Exception as exc:
        logger.error(f"Failed to fetch pending scans from repository: {exc}")
        return

    for scan in pending_scans:
        try:
            await scan_analysis_use_case.execute(scan_id=scan.id)
        except Exception as exc:
            logger.error(f"Failed processing automatic scan {scan.id}: {exc}")
            continue

def start_apscheduler():
    """defines the time frame for the scan execution
    using cron rules: minute hour dayOfTheMonth month dayOfTheWeek
    """
    scheduler.add_job(
        run_timeframe_scan_analysis,
        trigger="cron",
        hour=f"{settings.automatic_scan_start_hour}-{settings.automatic_scan_end_hour}",
        minute="0",
        id="aneurysm_idle_batch_job"
    )
    scheduler.start()