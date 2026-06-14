from fastapi import FastAPI
from app.routers import scans, hospital_settings

app = FastAPI(title = "Hospital Aneurysm Detection API")

app.include_router(scans.router)
# app.include_router(hospital_settings.router)