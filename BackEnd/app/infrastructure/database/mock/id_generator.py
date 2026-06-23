
from app.modules.identity_access.services import IdGenerator


class FakeIdGenerator(IdGenerator):
    def __init__(self):
        self._counter = 100000

    async def generate_6_digit_id(self) -> str:
        self._counter += 1
        return str(self._counter)[-6:].zfill(6)
