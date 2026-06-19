from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.dependencies import get_settings_repository
from app.config import settings
from app.routers import scans_route, auth_route, patient_route
from app.tasks.scheduler import start_apscheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown"""
    #before server is live

    # connect to DB
    client = AsyncIOMotorClient(settings.mongodb_uri) # Connect to MongoDB
    db = client[settings.mongodb_db_name] # Select the specific database
    app.state.db = db # Connect to CAD_DB database

    # pull initial settings from DB and cache in memory for quick access across the app:
    settings_repo = get_settings_repository(db)
    await settings_repo.get_settings() # Loads settings into the repository's internal cache
    
    start_apscheduler()

    yield #server is live
    
    #server is closed
    client.close()
    print("Stoping application services")

app = FastAPI(
    title = "Hospital Aneurysm Detection Web Orchestrator",
    lifespan = lifespan
    )

app.include_router(scans_route.router)
app.include_router(auth_route.router)
app.include_router(patient_route.router)


