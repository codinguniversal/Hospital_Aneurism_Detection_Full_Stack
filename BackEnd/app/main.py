from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
from motor.motor_asyncio import AsyncIOMotorClient

from app.dependencies import build_settings_repository, _ai_http_client
from app.config import settings
from app.routers import scans_route, auth_route, patient_route
from app.tasks.scheduler import start_apscheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown"""
    #before server is live

    # connect to DB
    if settings.database_mode == "mongodb":
        db_client = AsyncIOMotorClient(settings.mongodb_uri) # Connect to MongoDB
        db = db_client[settings.mongodb_db_name] # Select the specific database
        app.state.db = db # Connect to CAD_DB database
        app.state.http_client = httpx.AsyncClient()
    else:
        pass

    # pull initial settings from DB and cache in memory for quick access across the app:
    settings_repo = build_settings_repository()
    await settings_repo.get_settings() # cache's settings
    
    start_apscheduler()

    yield #server is live
    
    await _ai_http_client.aclose()
    #server is closed
    if settings.database_mode == "mongodb":
        db_client.close()
    
    print("Stoping application services")

app = FastAPI(
    title = "Hospital Aneurysm Detection Web Orchestrator",
    lifespan = lifespan
    )

app.include_router(scans_route.router)
app.include_router(auth_route.router)
app.include_router(patient_route.router)


