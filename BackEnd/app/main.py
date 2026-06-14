from fastapi import FastAPI
from app.routers import scans, hospital_settings

app = FastAPI(title = "Hospital Aneurysm Detection Web Orchestrator")

app.include_router(scans.router)
