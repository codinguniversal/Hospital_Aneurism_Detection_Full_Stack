from motor.motor_asyncio import AsyncIOMotorDatabase

from app.infrastructure.notifications.mail_trap_notifier import MailtrapEmailNotifier
from app.infrastructure.notifications.console_notifier import ConsoleNotifier
from app.core.patient_management.services import Notifier
from app.core.factory import InfrastructureFactory
from app.core.patient_management.repositories import Patients
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

    def patients(self) -> Patients:
        return MongoPatientRepository(
            db=self._db,
            storage_base_dir = static_settings.storage_base_dir,
            slice_meta_collection_name = static_settings.slice_meta_collection_name
            )

    def users(self) -> UserRepository:
        return MongoUserRepository(db=self._db)

    def settings(self) -> SettingsRepository:
        if self._settings_repo is None:
            self._settings_repo = MongoSettingsRepository(db=self._db)
        return self._settings_repo

    def id_generator(self) -> IdGenerator:
        self._id_generator = MongoIdGenerator(db=self._db)
        return self._id_generator
    
    def notifier(self)->Notifier:
        
        return MailtrapEmailNotifier(
            api_token=static_settings.mailtrap_api_token,
            inbox_id=static_settings.mailtrap_inbox_id,
            recipient_emails_str=static_settings.notification_recipients,
            sender_email=static_settings.sender_email
        )


class MockInfrastructureFactory(InfrastructureFactory):
    def __init__(self, mock_db: MockNoSQLDataLayer):
        self._mock_db = mock_db
        self._settings_repo = None

    def patients(self) -> Patients:
        return MockPatientRepository(db=self._mock_db)

    def users(self) -> UserRepository:
        return MockUserRepository(db=self._mock_db)

    def settings(self) -> SettingsRepository:
        if self._settings_repo is None:
            self._settings_repo = MockSettingsRepository(db=self._mock_db)
        return self._settings_repo

    def id_generator(self) -> IdGenerator:
        return FakeIdGenerator()
    
    def notifier(self) -> Notifier:
        return  ConsoleNotifier()
