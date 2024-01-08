from injector import inject

from src.modules.common.application.dependency import Dependency
from src.modules.student_management.domain import Student

from ..repositories import StudentRepository

__all__ = [
    "FindStudentQuery",
]


class FindStudentQuery(Dependency):
    _repository: StudentRepository

    @inject
    def __init__(self, repository: StudentRepository) -> None:
        self._repository = repository

    async def execute(self, telegram_id: int) -> Student | None:
        return await self._repository.find_by_id(telegram_id)
