from typing import final

from src.application.student_management.repositories import StudentRepository
from src.domain.student_management import Role, Student
from src.infrastructure.common.persistence import PostgresRepositoryImpl
from src.infrastructure.student_management.mappers import StudentMapper

__all__ = [
    "StudentRepositoryImpl",
]


@final
class StudentRepositoryImpl(PostgresRepositoryImpl, StudentRepository):
    _mapper: StudentMapper = StudentMapper()

    async def find_by_id(self, telegram_id: int) -> Student | None:
        query = """SELECT st.id, st.name, st.surname, st.role, st.group_id,
                 st.birthdate, st.is_checked_in_today, gr.name AS group_name, gr.university_id
                 FROM students AS st 
                 JOIN groups AS gr 
                 ON st.group_id = gr.id 
                 WHERE telegram_id = $1"""

        record = await self._con.fetchrow(query, telegram_id)

        if record is None:
            return None

        return self._mapper.to_domain(record)

    async def find_by_group_name_and_role(self, group_name: str, role: Role) -> Student | None:
        query = """SELECT st.name, st.surname, st.role, st.group_id,
                 st.birthdate, st.is_checked_in_today, gr.name AS group_name, gr.university_id
                 FROM students AS st 
                 JOIN groups AS gr 
                 ON st.group_id = gr.id 
                 WHERE gr.name LIKE $1 AND role = $2"""

        record = await self._con.fetchrow(query, group_name, role)

        if record is None:
            return None

        return self._mapper.to_domain(record)

    # async def create_and_return(
    #     self,
    #     student_raw: StudentLoginData,
    #     group_id: GroupId,
    # ) -> Student:
    #     query = (
    #         "INSERT INTO students "
    #         "(telegram_id, group_id, name, surname, role, birthdate) "
    #         "VALUES ($1, $2, $3, $4, $5, $6)"
    #     )
    #     await self._con.execute(
    #         query,
    #         student_raw.telegram_id,
    #         group_id,
    #         student_raw.name,
    #         student_raw.surname,
    #         student_raw.role,
    #         student_raw.birthdate,
    #     )
    #
    #     return Student(
    #         telegram_id=StudentId(student_raw.telegram_id),
    #         group_id=group_id,
    #         name=student_raw.name,
    #         surname=student_raw.surname,
    #         role=student_raw.role,
    #         birthdate=student_raw.birthdate,
    #     )
    #
    # async def all(self) -> list[Student]:
    #     query = "SELECT * FROM students"
    #     records = await self._con.fetch(query)
    #
    #     return [Student.from_mapping(record) for record in records]
    #
    # async def filter_group_by_id(self, group_id: GroupId) -> list[Student] | None:
    #     query = "SELECT * FROM students WHERE group_id = $1"
    #
    #     records = await self._con.fetch(query, group_id)
    #     return [Student.from_mapping(record) for record in records]
    #
    # async def update_surname_by_id(self, new_surname: str, student_id: StudentId) -> None:
    #     query = ("UPDATE students "
    #              "SET surname = $1 "
    #              "WHERE telegram_id = $2")
    #
    #     await self._con.execute(query, new_surname, student_id)
    #
    # async def update_name_by_id(self, new_name: str, student_id: StudentId) -> None:
    #     query = ("UPDATE students "
    #              "SET name = $1 "
    #              "WHERE telegram_id = $2")
    #
    #     await self._con.execute(query, new_name, student_id)
