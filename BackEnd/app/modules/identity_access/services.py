from abc import ABC, abstractmethod


class IdGenerator(ABC):
    @abstractmethod
    async def generate_6_digit_id(self) -> str:
        """atomic generation of unique 6-digit ID."""
        pass
