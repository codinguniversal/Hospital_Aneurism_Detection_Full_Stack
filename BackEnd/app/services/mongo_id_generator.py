from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.services import IdGenerator

class MongoIdGenerator(IdGenerator):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._collection = db["counters"]

    async def generate_6_digit_id(self) -> str:
        result = await self._collection.find_one_and_update(
            {"_id": "patient_id_sequence"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        
        # Start numbering from 100000 if it's a fresh database
        sequence_number = result.get("seq", 100000)
        
        # Ensures it wraps cleanly at 6 digits and strings are padded: e.g., "100001"
        return str(sequence_number)[-6:].zfill(6)