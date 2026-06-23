from abc import ABC, abstractmethod


class IdGenerator(ABC):
    @abstractmethod
    async def generate_6_digit_id(self) -> str:
        """atomic generation of unique 6-digit ID."""
        pass

class TokenManager(ABC):
    """Absract contract to handle authenticating tokens"""
    @abstractmethod
    def create_access_token(self, data:dict)->str:
        pass
    @abstractmethod
    def decode_access_token(self, token:str)->dict:
        pass