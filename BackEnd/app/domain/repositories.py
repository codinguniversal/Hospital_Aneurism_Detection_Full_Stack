from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import ScanEntity, UserEntity, PatientEntity

class UserRepository(ABC):
    @abstractmethod
    async def get_by_identifer(self, identifer:str) -> Optional[UserEntity]:
        """fetch complete userEntity or return None"""
        pass
class PatientRepository(ABC):
    # Patient Functiosn
    @abstractmethod
    async def get_all_patients(self) ->List[PatientEntity]:
        """returns all patients"""
        pass
    # Scan Functions
    @abstractmethod
    async def get_scan_binary_data(self, scan_id: str)-> bytes | None:
        """returns the dicom images  or None"""
        pass
    @abstractmethod
    async def get_all_pending_scans(self) -> List[ScanEntity]:
        """returns all scans that haven't been analysed yet"""
        pass
    @abstractmethod
    async def update_scan_results(self, scan_id: str, results: dict) -> None:
        """adds results to scan and updates its status"""
        pass
