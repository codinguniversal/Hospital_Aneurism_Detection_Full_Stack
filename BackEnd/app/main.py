from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 Added CORS Middleware import
import httpx
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.v1.routers import admin_settings_route, auth_route, email_check_route, patient_route, scans_route
from app.dependencies import build_settings_repository, _ai_http_client, initialize_infrastructure
from app.config import static_settings
from app.api.v1.routers import users_route
from app.infrastructure.scheduler.scheduler import start_apscheduler

import logging

# Configure logging to show INFO, WARNING, ERROR, CRITICAL
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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

# 🌐 ---- CORS POLICY MIDDLEWARE INTEGRATION ----
origins = [
    "http://localhost:5173",    # Vite local web server default port
    "http://127.0.0.1:5173",    # Local alternative network index mapping
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Intercepts and approves cross-origin script origins
    allow_credentials=True,
    allow_methods=["*"],         # Explicitly allows preflight OPTIONS along with POST/GET/PUT
    allow_headers=["*"],         # Allows custom authorization headers to pass cleanly
)
# -----------------------------------------------

app.include_router(scans_route.router)
app.include_router(auth_route.router)
app.include_router(email_check_route.router)
app.include_router(patient_route.router)
app.include_router(admin_settings_route.router)
app.include_router(users_route.router)