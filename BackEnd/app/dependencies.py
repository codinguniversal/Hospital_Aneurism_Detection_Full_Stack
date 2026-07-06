from typing import Optional
import httpx

from app.core.patient_management.services import Notifier, ScanAnalyzer
from app.config import static_settings
from app.core.patient_management.repositories import Patients
from app.core.patient_management.use_cases import (
    GetAllPatients,
    GetPatientDiagnosticReport,
    DetectAneurysmProbabilities,
    GetSliceImage,
)
from app.infrastructure.ai.ai_client import HTTPXScanAnalysisService
from app.infrastructure.ai.mock_ai_client import MockScanAnalysisService
from app.core.factory import InfrastructureFactory
from app.infrastructure.database.mock.data_layer import MockNoSQLDataLayer
from app.infrastructure.factories import MockInfrastructureFactory, MongoInfrastructureFactory
from app.modules.identity_access.repositories import UserRepository
from app.modules.identity_access.services import IdGenerator
from app.modules.identity_access.use_cases import (
    AuthenticateUserUseCase,
    CheckEmailUseCase,
    DeleteUserByIdUseCase,
    GetAllUsersUseCase,
    RegisterUserUseCase,
)
from app.modules.system_settings.repositories import SettingsRepository
from app.modules.system_settings.use_cases import GetSettingsUseCase, UpdateSettingsUseCase
from motor.motor_asyncio import AsyncIOMotorDatabase

_factory: Optional[InfrastructureFactory] = None
_ai_http_client = None

def initialize_infrastructure(db: Optional[AsyncIOMotorDatabase] = None):
    global _factory
    if static_settings.database_mode == "mongodb":
        if db is None:
            raise ValueError("Mongodb mode requires a db connection")
        _factory = MongoInfrastructureFactory(db=db)
    else:
        mock_db = MockNoSQLDataLayer()
        _factory = MockInfrastructureFactory(mock_db=mock_db)


def get_ai_http_client() -> httpx.AsyncClient:
    global _ai_http_client
    if _ai_http_client is None:
        _ai_http_client = httpx.AsyncClient()
    return _ai_http_client


async def build_ai_service() -> ScanAnalyzer:
    patient_repo = build_patient_repository()
    if static_settings.use_mock_ai:
        return MockScanAnalysisService(patient_repo = patient_repo ,
                                    fixed_overall_probability=0.85)

    settings_repo = build_settings_repository()
    dynamic_settings = await settings_repo.get_settings()
    return HTTPXScanAnalysisService(
        patient_repo = patient_repo,
        client=get_ai_http_client(),
        base_url=str(dynamic_settings.ai_api_url),
        timeout=dynamic_settings.ai_timeout_limit,
    )


async def build_id_generator() -> IdGenerator:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized.")
    return _factory.id_generator()


def build_patient_repository() -> Patients:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized. Call initialize_infrastructure() first.")
    return _factory.patients()


def build_user_repository() -> UserRepository:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized. Call initialize_infrastructure() first.")
    return _factory.users()


def build_settings_repository() -> SettingsRepository:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized. Call initialize_infrastructure() first.")
    return _factory.settings()


def build_get_patient_records_use_case() -> GetAllPatients:
    patient_repo = build_patient_repository()
    settings_repo = build_settings_repository()
    return GetAllPatients(
        patient_repo=patient_repo,
        settings_repo=settings_repo,
    )


def build_get_patient_results_use_case() -> GetPatientDiagnosticReport:
    patient_repo = build_patient_repository()
    return GetPatientDiagnosticReport(patient_repo=patient_repo)

def build_notification_service() -> Notifier:
    if _factory is None:
        raise RuntimeError("Infrastructure not initialized. Call initialize_infrastructure() first.")
    return _factory.notifier()

async def build_scan_analysis_use_case() -> DetectAneurysmProbabilities:
    patient_repo = build_patient_repository()
    ai_service = await build_ai_service()
    notification_service = build_notification_service()
    settings_repo = build_settings_repository()

    return DetectAneurysmProbabilities(
        patient_repo=patient_repo,
        ai_service=ai_service,
        notifier= notification_service,
        settings_repo=settings_repo
    )
async def build_get_slice_image_use_case()->GetSliceImage:
    patient_repo = build_patient_repository()
    return GetSliceImage(patient_repo= patient_repo)


def build_authenticate_user_use_case() -> AuthenticateUserUseCase:
    user_repo = build_user_repository()
    return AuthenticateUserUseCase(user_repo=user_repo)


async def build_register_user_use_case() -> RegisterUserUseCase:
    user_repo = build_user_repository()
    id_generator = await build_id_generator()
    return RegisterUserUseCase(user_repo=user_repo, id_service=id_generator)


def build_check_email_use_case() -> CheckEmailUseCase:
    user_repo = build_user_repository()
    return CheckEmailUseCase(user_repo=user_repo)


def build_update_settings_use_case() -> UpdateSettingsUseCase:
    settings_repo = build_settings_repository()
    return UpdateSettingsUseCase(settings_repo=settings_repo)


def build_get_settings_use_case() -> GetSettingsUseCase:
    settings_repo = build_settings_repository()
    return GetSettingsUseCase(settings_repo=settings_repo)


def build_get_all_users_use_case() -> GetAllUsersUseCase:
    user_repo = build_user_repository()
    return GetAllUsersUseCase(user_repo=user_repo)


def build_delete_user_by_id_use_case() -> DeleteUserByIdUseCase:
    user_repo = build_user_repository()
    return DeleteUserByIdUseCase(user_repo=user_repo)

# --- fast api wrappers ---
# async def get_patient_records_use_case(
#     use_case: GetAllPatientsUseCase = Depends(build_get_patient_records_use_case),
# ) -> GetAllPatientsUseCase:
#     return use_case


# async def get_patient_results_use_case(
#     use_case: GetPatientResultsUseCase = Depends(build_get_patient_results_use_case),
# ) -> GetPatientResultsUseCase:
#     return use_case


# async def get_scan_analysis_use_case(
#     use_case: ScanAnalysisUseCase = Depends(build_scan_analysis_use_case),
# ) -> ScanAnalysisUseCase:
#     return use_case


# async def get_authenticate_user_use_case(
#     use_case: AuthenticateUserUseCase = Depends(build_authenticate_user_use_case),
# ) -> AuthenticateUserUseCase:
#     return use_case


# async def get_register_user_use_case(
#     use_case: RegisterUserUseCase = Depends(build_register_user_use_case),
# ) -> RegisterUserUseCase:
#     return use_case


# async def get_check_email_use_case(
#     use_case: CheckEmailUseCase = Depends(build_check_email_use_case),
# ) -> CheckEmailUseCase:
#     return use_case


# async def get_update_settings_use_case(
#     use_case: UpdateSettingsUseCase = Depends(build_update_settings_use_case),
# ) -> UpdateSettingsUseCase:
#     return use_case


# async def get_settings_use_case(
#     use_case: GetSettingsUseCase = Depends(build_get_settings_use_case),
# ) -> GetSettingsUseCase:
#     return use_case


# async def get_all_users_use_case(
#     use_case: GetAllUsersUseCase = Depends(build_get_all_users_use_case),
# ) -> GetAllUsersUseCase:
#     return use_case


# async def delete_user_by_id_use_case(
#     use_case: DeleteUserByIdUseCase = Depends(build_delete_user_by_id_use_case),
# ) -> DeleteUserByIdUseCase:
#     return use_case

