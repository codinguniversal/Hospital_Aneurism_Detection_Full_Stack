from fastapi import Depends, Request
from app.config import settings
from app.domain.repositories import PatientRepository, UserRepository 
from app.repositories.Mongo_patient_repository import MongoPatientRepository
from app.repositories.mock_patient_repository import MockPatientRepository
from app.repositories.mock_user_repository import MockUserRepository
from app.services.mock_data_layer import MockNoSQLDataLayer, get_data_layer
from app.services.ai_service import AIService, get_ai_service

# Use Case Imports
from app.usecases.get_patient_records_use_case import GetPatientRecordsUseCase
from app.usecases.scan_analysis_use_case import ScanAnalysisUseCase
from app.usecases.auth_user_use_case import AuthenticateUserUseCase
from app.usecases.register_user_use_case import RegisterUserUseCase
from app.usecases.get_patient_results_use_case import GetPatientResultsUseCase

# --- database session extractor ---
def get_db(request: Request):
    """Extracts the live MongoDB connection from FastAPI's request state"""
    return request.app.state.db

# --- Repository Factories ---

def get_patient_repository(
    request: Request,
    db = Depends(get_data_layer)
) -> PatientRepository:
    if settings.database_mode == "mongodb":
        # Reconstitutes the Mongo repository using the live DB session [1]
        return MongoPatientRepository(db=request.app.state.db)
    
    # Returns the Mock implementation for development [2]
    return MockPatientRepository(data_layer=db)

def get_user_repository(
    mock_data = Depends(get_data_layer)
) -> UserRepository:
    # Currently returns Mock; can be easily updated for Mongo similarly to above
    return MockUserRepository(data_layer=mock_data)


# --- Use Case Factories ---

def get_patient_records_use_case(
    patient_repo: PatientRepository = Depends(get_patient_repository)
) -> GetPatientRecordsUseCase:
    return GetPatientRecordsUseCase(patient_repo=patient_repo)

def get_scan_analysis_use_case(
    patient_repo: PatientRepository = Depends(get_patient_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> ScanAnalysisUseCase:
    return ScanAnalysisUseCase(patient_repo=patient_repo, ai_service=ai_service)

def get_authenticate_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(user_repo=user_repo)

def get_register_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository)
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo=user_repo)

def get_patient_results_use_case(
    patient_repo: PatientRepository = Depends(get_patient_repository)
) -> GetPatientResultsUseCase:
    return GetPatientResultsUseCase(patient_repo=patient_repo)
