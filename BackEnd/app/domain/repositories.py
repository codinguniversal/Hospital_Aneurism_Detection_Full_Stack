from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities import UserEntity

class UserRepository(ABC):
    @abstractmethod
    async def get_by_identifer(self, identifer:str) -> Optional[UserEntity]:
        """fetch complete userEntity or return None"""
        pass
class ScanRepository(ABC):
    @abstractmethod
    async def get_scan_binary_data(self, scan_id: str)-> bytes | None:
        """returns the dicom images  or None"""
        pass
    @abstractmethod
    async def get_all_pending_scans(self):
        """returns all scans that haven't been analysed yet"""
        pass
    @abstractmethod
    async def update_scan_results(self, scan_id: str, results: dict):
        """adds results to scan and updates its status"""
        pass
