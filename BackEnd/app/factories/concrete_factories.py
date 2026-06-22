from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.factories import InfrastructureFactory
from app.domain.repositories import PatientRepository, UserRepository, SettingsRepository

# Mongo Repos
from app.repositories.mongo_repos.mongo_settings_repository import MongoSettingsRepository
from app.repositories.mongo_repos.mongo_user_repository import MongoUserRepository
from app.repositories.mongo_repos.Mongo_patient_repository import MongoPatientRepository

# mock repositories
from app.repositories.mock_repos.mock_patient_repository import MockPatientRepository
from app.repositories.mock_repos.mock_user_repository import MockUserRepository
from app.repositories.mock_repos.mock_settings_repository import MockSettingsRepository

# mock data layer
from app.services.mock_data_layer import MockNoSQLDataLayer

class MongoInfrastructureFactory(InfrastructureFactory):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._settings_repo = None

    def get_patient_repository(self) -> PatientRepository:
        return MongoPatientRepository(db = self._db)
    
    def get_user_repository(self) -> UserRepository:
        return MongoUserRepository(db=self._db)

    def get_settings_repository(self) -> SettingsRepository:
        if self.settings_repo is None:
            self.settings_repo =MongoSettingsRepository(db=self._db)
        return self.settings_repo
    
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