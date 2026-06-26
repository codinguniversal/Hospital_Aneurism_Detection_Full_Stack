from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.factory import InfrastructureFactory
from app.core.patient_management.repositories import PatientRepository
from app.infrastructure.database.mock.data_layer import MockNoSQLDataLayer
from app.infrastructure.database.mock.id_generator import FakeIdGenerator
from app.infrastructure.database.mock.patient_repository import MockPatientRepository
from app.infrastructure.database.mock.settings_repository import MockSettingsRepository
from app.infrastructure.database.mock.user_repository import MockUserRepository
from app.infrastructure.database.mongo.id_generator import MongoIdGenerator
from app.infrastructure.database.mongo.patient_repository import MongoPatientRepository
from app.infrastructure.database.mongo.settings_repository import MongoSettingsRepository
from app.infrastructure.database.mongo.user_repository import MongoUserRepository
from app.modules.identity_access.repositories import UserRepository
from app.modules.identity_access.services import IdGenerator
from app.modules.system_settings.repositories import SettingsRepository
from app.config import static_settings

class MongoInfrastructureFactory(InfrastructureFactory):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._settings_repo = None
        self._id_generator = None

    def get_patient_repository(self) -> PatientRepository:
        return MongoPatientRepository(
            db=self._db,
            storage_base_dir = static_settings.storage_base_dir,
            slice_meta_collection_name = static_settings.slice_meta_collection_name
            )

    def get_user_repository(self) -> UserRepository:
        return MongoUserRepository(db=self._db)

    def get_settings_repository(self) -> SettingsRepository:
        if self._settings_repo is None:
            self._settings_repo = MongoSettingsRepository(db=self._db)
        return self._settings_repo

    def get_id_generator(self) -> IdGenerator:
        self._id_generator = MongoIdGenerator(db=self._db)
        return self._id_generator


class MockInfrastructureFactory(InfrastructureFactory):
    def __init__(self, mock_db: MockNoSQLDataLayer):
        self._mock_db = mock_db
        self._settings_repo = None

    def get_patient_repository(self) -> PatientRepository:
        return MockPatientRepository(db=self._mock_db)

    def get_user_repository(self) -> UserRepository:
        return MockUserRepository(db=self._mock_db)

    def get_settings_repository(self) -> SettingsRepository:
        if self._settings_repo is None:
            self._settings_repo = MockSettingsRepository(db=self._mock_db)
        return self._settings_repo

    def get_id_generator(self) -> IdGenerator:
        return FakeIdGenerator()
