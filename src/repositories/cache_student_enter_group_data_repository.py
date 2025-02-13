from typing import Final, final

from src.common.repositories import RedisRepository
from src.dto import StudentEnterGroupDTO

__all__ = [
    "CacheStudentEnterGroupRepository",
]


@final
class CacheStudentEnterGroupRepository(RedisRepository):
    _SECONDS_TO_EXPIRE: Final[int] = 24 * 60 * 60 * 7  # 1 week

    async def cache(self, data: StudentEnterGroupDTO) -> None:
        mapped_data = data.to_redis_dict()

        await self._con.hmset(mapped_data["telegram_id"], mapped_data)
        await self._con.expire(mapped_data["telegram_id"], self._SECONDS_TO_EXPIRE)

    async def fetch(self, telegram_id: int) -> StudentEnterGroupDTO | None:
        record = await self._con.hgetall(str(telegram_id))
        if record:
            return StudentEnterGroupDTO.from_redis_dict(record)
        return None

    async def delete(self, telegram_id: int) -> None:
        student_data = await self._con.hgetall(str(telegram_id))
        await self._con.hdel(str(telegram_id), *student_data)
