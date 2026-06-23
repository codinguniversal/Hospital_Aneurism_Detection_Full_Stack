from abc import ABC, abstractmethod

from app.core.patient_management.repositories import PatientRepository
from app.modules.identity_access.repositories import UserRepository
from app.modules.identity_access.services import IdGenerator
from app.modules.system_settings.repositories import SettingsRepository


class InfrastructureFactory(ABC):
    @abstractmethod
    def get_patient_repository(self) -> PatientRepository:
        pass

    @abstractmethod
    def get_user_repository(self) -> UserRepository:
        pass

    @abstractmethod
    def get_settings_repository(self) -> SettingsRepository:
        pass

    @abstractmethod
    def get_id_generator(self) -> IdGenerator:
        pass
