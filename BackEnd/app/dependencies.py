from typing import Optional, cast
from fastapi import Depends
import httpx


from app.config import static_settings
from app.domain.repositories import PatientRepository, SettingsRepository, UserRepository
from app.domain.services import IdGenerator 
from app.domain.factories import InfrastructureFactory

from app.repositories.mongo_repos.mongo_user_repository import MongoUserRepository
from app.repositories.mongo_repos.mongo_settings_repository import MongoSettingsRepository
from app.repositories.mongo_repos.Mongo_patient_repository import MongoPatientRepository
from app.repositories.mock_repos.mock_patient_repository import MockPatientRepository
from app.repositories.mock_repos.mock_settings_repository import MockSettingsRepository
from app.repositories.mock_repos.mock_user_repository import MockUserRepository

from app.services.mock_data_layer import  MockNoSQLDataLayer
from app.services.mock_ai_service import MockScanAnalysisService
from app.services.ai_service import HTTPXScanAnalysisService
from app.services.mock_id_generator import FakeIdGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase

# Use Case Imports
from app.usecases.settings_use_cases.get_settings_use_case import GetSettingsUseCase
from app.usecases.settings_use_cases.update_setings_use_case import UpdateSettingsUseCase
from app.usecases.patient_use_cases.get_all_patients_use_case import GetAllPatientsUseCase
from app.usecases.scan_use_cases.scan_analysis_use_case import ScanAnalysisUseCase
from app.usecases.auth_use_cases.auth_user_use_case import AuthenticateUserUseCase
from app.usecases.auth_use_cases.register_user_use_case import RegisterUserUseCase
from app.usecases.auth_use_cases.check_email_use_case import CheckEmailUseCase
from app.usecases.patient_use_cases.get_patient_results_use_case import GetPatientResultsUseCase

from app.factories.concrete_factories import MongoInfrastructureFactory, MockInfrastructureFactory



# Singleton HTTP client for the whole app
_factory: Optional[InfrastructureFactory] = None
_ai_http_client = None
_id_generator = None

def initialize_infrastructure(db: Optional[AsyncIOMotorDatabase] = None):
    global _factory
    if static_settings.database_mode == "mongodb":
        if db is None:
            raise ValueError("Mongodb mode requires a db connection")
        _factory = MongoInfrastructureFactory(db=db)
    else:
        mock_db = MockNoSQLDataLayer()
        _factory = MockInfrastructureFactory(mock_db= mock_db)

def get_ai_http_client() -> httpx.AsyncClient:
    global _ai_http_client
    if _ai_http_client is None:
        _ai_http_client = httpx.AsyncClient()
    return _ai_http_client



async def build_ai_service():
    if static_settings.use_mock_ai:
        return MockScanAnalysisService(fixed_overall_probability= 0.85)

    settings_repo = build_settings_repository()
    dynamic_settings = await settings_repo.get_settings()
    return HTTPXScanAnalysisService(
        client = get_ai_http_client(),
        base_url= str(dynamic_settings.ai_api_url),
        timeout= dynamic_settings.ai_timeout_limit
        )
async def build_id_generator() -> IdGenerator:
    global _id_generator
    if _id_generator is None:
        _id_generator = FakeIdGenerator() 
    return _id_generator  

#--- Repository Builders ---
def build_patient_repository()-> PatientRepository:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized. Call initialize_infrastructure() first.")
    return _factory.get_patient_repository()

def build_user_repository()-> UserRepository:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized. Call initialize_infrastructure() first.")
    return _factory.get_user_repository()

def build_settings_repository()->SettingsRepository:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized. Call initialize_infrastructure() first.")
    return _factory.get_settings_repository()

#--- Use Case Builders ---
def build_get_patient_records_use_case() -> GetAllPatientsUseCase:
    patient_repo = build_patient_repository()
    settings_repo = build_settings_repository()
    return GetAllPatientsUseCase(
        patient_repo=patient_repo,
        settings_repo=settings_repo
    )

def build_get_patient_results_use_case() -> GetPatientResultsUseCase:
    patient_repo = build_patient_repository()
    return GetPatientResultsUseCase(patient_repo=patient_repo)

async def build_scan_analysis_use_case() -> ScanAnalysisUseCase:
    patient_repo = build_patient_repository()
    ai_service = await build_ai_service()          # assuming get_ai_service is a manual builder itself
    return ScanAnalysisUseCase(
        patient_repo=patient_repo,
        ai_service=ai_service
    )

def build_authenticate_user_use_case() -> AuthenticateUserUseCase:
    user_repo = build_user_repository()
    return AuthenticateUserUseCase(user_repo=user_repo)

async def build_register_user_use_case() -> RegisterUserUseCase:
    user_repo = build_user_repository()
    id_generator = await build_id_generator()
    return RegisterUserUseCase(user_repo=user_repo, id_service= id_generator)

def build_check_email_use_case() -> CheckEmailUseCase:
    user_repo = build_user_repository()
    return CheckEmailUseCase(user_repo=user_repo)

def build_update_settings_use_case() -> UpdateSettingsUseCase:
    settings_repo = build_settings_repository()
    return UpdateSettingsUseCase(settings_repo=settings_repo)

def build_get_settings_use_case() -> GetSettingsUseCase:
    settings_repo = build_settings_repository()
    return GetSettingsUseCase(settings_repo=settings_repo)

# --- Fast API Wrapeprs for Use Cases ---
async def get_patient_records_use_case(
    use_case: GetAllPatientsUseCase = Depends(build_get_patient_records_use_case)
) -> GetAllPatientsUseCase:
    return use_case

async def get_patient_results_use_case(
    use_case: GetPatientResultsUseCase = Depends(build_get_patient_results_use_case)
) -> GetPatientResultsUseCase:
    return use_case

async def get_scan_analysis_use_case(
    use_case: ScanAnalysisUseCase = Depends(build_scan_analysis_use_case)
) -> ScanAnalysisUseCase:
    return use_case

async def get_authenticate_user_use_case(
    use_case: AuthenticateUserUseCase = Depends(build_authenticate_user_use_case)
) -> AuthenticateUserUseCase:
    return use_case

async def get_register_user_use_case(
    use_case: RegisterUserUseCase = Depends(build_register_user_use_case)
) -> RegisterUserUseCase:
    return use_case

async def get_check_email_use_case(
    use_case: CheckEmailUseCase = Depends(build_check_email_use_case)
) -> CheckEmailUseCase:
    return use_case

async def get_update_settings_use_case(
    use_case: UpdateSettingsUseCase = Depends(build_update_settings_use_case)
) -> UpdateSettingsUseCase:
    return use_case

async def get_settings_use_case(
    use_case: GetSettingsUseCase = Depends(build_get_settings_use_case)
) -> GetSettingsUseCase:
    return use_case
