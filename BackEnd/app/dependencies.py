from typing import Any

from fastapi import Depends, Request
from app.usecases.settings_use_cases.update_setings_use_case import UpdateSettingsUseCase
from app.config import settings
from app.domain.repositories import PatientRepository, SettingsRepository, UserRepository 
from app.repositories.Mongo_patient_repository import MongoPatientRepository
from app.repositories.mock_patient_repository import MockPatientRepository
from app.repositories.mock_settings_repository import MockSettingsRepository
from app.repositories.mock_user_repository import MockUserRepository
from app.services.mock_data_layer import  get_data_layer, MockNoSQLDataLayer
from app.services.ai_service import AIService, get_ai_service

# Use Case Imports
from app.usecases.patient_use_cases.get_patient_records_use_case import GetPatientRecordsUseCase
from app.usecases.scan_use_cases.scan_analysis_use_case import ScanAnalysisUseCase
from app.usecases.auth_use_cases.auth_user_use_case import AuthenticateUserUseCase
from app.usecases.auth_use_cases.register_user_use_case import RegisterUserUseCase
from app.usecases.patient_use_cases.get_patient_results_use_case import GetPatientResultsUseCase

 

# Single instance of the mock data layer for development/testing
_mock_db_service = MockNoSQLDataLayer() 

# --- database session extractor ---
def _get_db_connection():
    """Helper to retrieve teh current DB connection"""
    if settings.database_mode == "mongodb":
        from app.main import app
        return app.state.db
    
    return _mock_db_service 

#--- Repository Builders ---
def build_patient_repository()-> PatientRepository:
    db = _get_db_connection()
    if settings.database_mode == "mongodb":
        return MongoPatientRepository(db=db)
    return MockPatientRepository(db = db)

def build_user_repository()-> UserRepository:
    db = _get_db_connection()
    if settings.database_mode == "mongodb":
        # return MongoUserRepository(db = db) # implement when ready
        pass
    return MockUserRepository(db=db)

def build_settings_repository()->SettingsRepository:
    db = _get_db_connection()
    if settings.database_mode == "mongodb":
        # return MongoSettingsRepository(db=db)   # implement when ready
        pass
    return MockSettingsRepository(db=db)

#--- Use Case Builders ---
def build_get_patient_records_use_case() -> GetPatientRecordsUseCase:
    patient_repo = build_patient_repository()
    settings_repo = build_settings_repository()
    return GetPatientRecordsUseCase(
        patient_repo=patient_repo,
        settings_repo=settings_repo
    )

def build_get_patient_results_use_case() -> GetPatientResultsUseCase:
    patient_repo = build_patient_repository()
    return GetPatientResultsUseCase(patient_repo=patient_repo)

def build_scan_analysis_use_case() -> ScanAnalysisUseCase:
    patient_repo = build_patient_repository()
    ai_service = get_ai_service()          # assuming get_ai_service is a manual builder itself
    return ScanAnalysisUseCase(
        patient_repo=patient_repo,
        ai_service=ai_service
    )

def build_authenticate_user_use_case() -> AuthenticateUserUseCase:
    user_repo = build_user_repository()
    return AuthenticateUserUseCase(user_repo=user_repo)

def build_register_user_use_case() -> RegisterUserUseCase:
    user_repo = build_user_repository()
    return RegisterUserUseCase(user_repo=user_repo)

def build_update_settings_use_case() -> UpdateSettingsUseCase:
    settings_repo = build_settings_repository()
    return UpdateSettingsUseCase(settings_repo=settings_repo)

# --- Fast API Wrapeprs for Use Cases ---
async def get_patient_records_use_case(
    use_case: GetPatientRecordsUseCase = Depends(build_get_patient_records_use_case)
) -> GetPatientRecordsUseCase:
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

async def get_update_settings_use_case(
    use_case: UpdateSettingsUseCase = Depends(build_update_settings_use_case)
) -> UpdateSettingsUseCase:
    return use_case
