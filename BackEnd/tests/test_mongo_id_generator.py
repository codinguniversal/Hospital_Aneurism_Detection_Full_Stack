import pytest

from app.infrastructure.database.mongo.id_generator import MongoIdGenerator


class FakeUsersCollection:
    async def find_one(self, *args, **kwargs):
        return {"employee_id": "000003"}


class FakeCountersCollection:
    def __init__(self):
        self.sequence = 1

    async def update_one(self, query, update, upsert=False):
        self.sequence = max(self.sequence, update["$max"]["seq"])

    async def find_one_and_update(self, query, update, **kwargs):
        self.sequence += update["$inc"]["seq"]
        return {"_id": query["_id"], "seq": self.sequence}


class FakeDatabase:
    def __init__(self):
        self.collections = {
            "users": FakeUsersCollection(),
            "counters": FakeCountersCollection(),
        }

    def __getitem__(self, name):
        return self.collections[name]


@pytest.mark.asyncio
async def test_generator_advances_stale_counter_past_seeded_users():
    generator = MongoIdGenerator(FakeDatabase())

    assert await generator.generate_6_digit_id() == "000004"
    assert await generator.generate_6_digit_id() == "000005"
