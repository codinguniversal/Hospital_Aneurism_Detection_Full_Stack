from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.modules.identity_access.services import IdGenerator


class MongoIdGenerator(IdGenerator):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._collection = db["counters"]
        self._users_collection = db["users"]

    async def generate_6_digit_id(self) -> str:
        # Users may be inserted by the seed script or imported independently of
        # the counter. Bring the counter forward before incrementing it so a
        # missing/stale counter can never regenerate an existing employee ID.
        highest_user = await self._users_collection.find_one(
            {"employee_id": {"$regex": r"^\d{6}$"}},
            sort=[("employee_id", -1)],
            projection={"employee_id": 1},
        )
        highest_employee_id = int(highest_user["employee_id"]) if highest_user else 0

        await self._collection.update_one(
            {"_id": "employee_id_sequence"},
            {"$max": {"seq": highest_employee_id}},
            upsert=True,
        )

        result = await self._collection.find_one_and_update(
            {"_id": "employee_id_sequence"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        sequence_number = result["seq"]
        if sequence_number > 999999:
            raise RuntimeError("The six-digit employee ID range has been exhausted.")

        return f"{sequence_number:06d}"
