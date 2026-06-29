from abc import ABC, abstractmethod

from app.core.patient_management.services import Notifier
from app.core.patient_management.repositories import Patients
from app.modules.identity_access.repositories import UserRepository
from app.modules.identity_access.services import IdGenerator
from app.modules.system_settings.repositories import SettingsRepository


class InfrastructureFactory(ABC):
    @abstractmethod
    def patients(self) -> Patients:
        pass

    @abstractmethod
    def users(self) -> UserRepository:
        pass

    @abstractmethod
    def settings(self) -> SettingsRepository:
        pass

    @abstractmethod
    def id_generator(self) -> IdGenerator:
        pass

    @abstractmethod
    def notifier(self) -> Notifier:
        pass
