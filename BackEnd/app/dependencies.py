from fastapi import Depends
from app.domain.repositories import PatientRepository, UserRepository
from app.repositories.mock_patient_repository import MockPatientRepository
from app.repositories.mock_user_repository import MockUserRepository
from app.services.mock_data_layer import NoSQLDataLayer, get_data_layer
from app.services.ai_service import AIService, get_ai_service

# Use Case Imports
from app.usecases.get_patient_records_use_case import GetPatientRecordsUseCase
from app.usecases.scan_analysis_use_case import ScanAnalysisUseCase
from app.usecases.auth_user_use_case import AuthenticateUserUseCase
from app.usecases.register_user_use_case import RegisterUserUseCase
from app.usecases.get_patient_results_use_case import GetPatientResultsUseCase

# --- Repository Factories ---

def get_patient_repository(
    data_layer: NoSQLDataLayer = Depends(get_data_layer)
) -> PatientRepository:
    return MockPatientRepository(data_layer=data_layer)

def get_user_repository(
    data_layer: NoSQLDataLayer = Depends(get_data_layer)
) -> UserRepository:
    return MockUserRepository(data_layer=data_layer)

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
