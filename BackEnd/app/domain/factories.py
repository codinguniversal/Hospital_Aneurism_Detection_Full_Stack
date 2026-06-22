from abc import ABC , abstractmethod

from app.domain.repositories import PatientRepository, SettingsRepository, UserRepository

class InfrastructureFactory(ABC):
    @abstractmethod
    def get_patient_repository(self) -> PatientRepository:
        pass

    @abstractmethod
    def get_user_repository(self)-> UserRepository:
        pass

    @abstractmethod
    def get_settings_repository(self)-> SettingsRepository:
        pass
