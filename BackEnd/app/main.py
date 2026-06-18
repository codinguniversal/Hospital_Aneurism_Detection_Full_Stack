from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import scans_route, auth_route, patient_route
from app.tasks.scheduler import start_apscheduler
from motor.motor_asyncio import AsyncIOMotorClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown"""

    client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.state.db = client["CAD_DB"] # Connect to CAD_DB database
    #before server is live
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


