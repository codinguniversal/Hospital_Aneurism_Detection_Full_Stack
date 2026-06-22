from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx
from motor.motor_asyncio import AsyncIOMotorClient

from app.routers import admin_settings_route
from app.dependencies import build_settings_repository, _ai_http_client, initialize_infrastructure
from app.config import static_settings
from app.routers import scans_route, auth_route, patient_route, email_check_route
from app.tasks.scheduler import start_apscheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown"""
    #before server is live

    # connect to DB
    if static_settings.database_mode == "mongodb":
        db_client = AsyncIOMotorClient(static_settings.mongodb_uri) # Connect to MongoDB
        db = db_client[static_settings.mongodb_db_name] # Select the specific database
        app.state.db = db # Connect to CAD_DB database
    else:
        db = None

    initialize_infrastructure(db)

    # pull initial settings from DB and cache in memory for quick access across the app:
    settings_repo = build_settings_repository()
    await settings_repo.get_settings() # cache's settings
    
    await start_apscheduler()

    yield #server is live
    
    if _ai_http_client is not None:
        await _ai_http_client.aclose()
    #server is closed
    if static_settings.database_mode == "mongodb":
        db_client.close()
    
    print("Stoping application services")

app = FastAPI(
    title = "Hospital Aneurysm Detection Web Orchestrator",
    lifespan = lifespan
    )

app.include_router(scans_route.router)
app.include_router(auth_route.router)
app.include_router(email_check_route.router)
app.include_router(patient_route.router)
app.include_router(admin_settings_route.router)


