from asyncio import TaskGroup
from typing import final

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from loguru import logger

from src.bot.poll_attendance.resources.inline_buttons import update_attendance_buttons
from src.bot.poll_attendance.resources.templates import (
    POLL_TEMPLATE,
    student_was_not_polled_warning_template,
)
from src.modules.attendance.application.queries import GetStudentAttendanceQuery
from src.modules.common.application.bot_notifier import BotNotifier
from src.modules.common.infrastructure.config import DEBUG
from src.modules.common.infrastructure.container import Container
from src.modules.common.infrastructure.scheduling import AsyncJob
from src.modules.edu_info.application.queries import (
    FetchUniTimezonByGroupIdQuery,
    GetAllGroupsQuery,
)
from src.modules.edu_info.domain import Group
from src.modules.student_management.application.commands import (
    DeleteStudentByTGIDCommand,
)
from src.modules.student_management.application.queries import (
    FindGroupHeadmanQuery,
    GetStudentsInfoFromGroupQuery,
)
from src.modules.student_management.domain import StudentInfo

__all__ = [
    "SendingJob",
]


@final
class SendingJob(AsyncJob):
    """Send everyone message which allow user to choose lessons which will be visited."""

    _bot: Bot
    _build_container: Container

    def __init__(
        self,
        bot: Bot,
    ) -> None:
        self._bot = bot

        if not DEBUG:
            self._trigger = "cron"
            self._trigger_args = {
                "hour": 7,
                "minute": 00,
                "day_of_week": "mon-sat",
            }

    async def __call__(self) -> None:
        async with Container() as container:
            get_all_groups_query = container.get_dependency(GetAllGroupsQuery)
            groups = await get_all_groups_query.execute()
            get_students_info_from_group_query = container.get_dependency(
                GetStudentsInfoFromGroupQuery,
            )
            delete_student_by_tg_id = container.get_dependency(DeleteStudentByTGIDCommand)

            fetch_group_timezone = container.get_dependency(FetchUniTimezonByGroupIdQuery)
            find_group_headman_query = container.get_dependency(FindGroupHeadmanQuery)
            notifier = container.get_dependency(BotNotifier)

            for group in groups:
                try:
                    timezone = await fetch_group_timezone.execute(group.id)
                    await self._send_to_group(
                        group,
                        delete_student_by_tg_id,
                        get_students_info_from_group_query,
                        find_group_headman_query,
                        timezone,
                    )
                except Exception as e:
                    await notifier.notify_about_job_exception(
                        e,
                        self.__class__.__name__,
                    )

    async def _send_to_group(
        self,
        group: Group,
        delete_student_by_tg_id: DeleteStudentByTGIDCommand,
        get_students_info_from_group_query: GetStudentsInfoFromGroupQuery,
        find_group_headman_query: FindGroupHeadmanQuery,
        timezone: str,
    ) -> None:
        students_info = await get_students_info_from_group_query.execute(group.id)
        group_headman = await find_group_headman_query.execute(group.id)

        async with TaskGroup() as tg:
            for student_info in students_info:
                tg.create_task(
                    self._send_to_student(
                        student_info,
                        delete_student_by_tg_id,
                        group_headman.telegram_id,
                        timezone,
                    ),
                )

    async def _send_to_student(
        self,
        student_info: StudentInfo,
        delete_student_by_tg_id: DeleteStudentByTGIDCommand,
        headman_telegram_id: int,
        timezone: str,
    ) -> None:
        async with Container() as container:
            try:
                get_student_attendance_query = container.get_dependency(GetStudentAttendanceQuery)
                attendances = await get_student_attendance_query.execute(
                    student_info.id,
                )

                if len(attendances) == 0:
                    return

                try:
                    await self._bot.send_message(
                        student_info.telegram_id,
                        POLL_TEMPLATE,
                        reply_markup=update_attendance_buttons(
                            student_info.attendance_noted,
                            attendances,
                            timezone,
                        ),
                    )
                except TelegramForbiddenError:
                    logger.error(student_info)
                    await self._bot.send_message(
                        headman_telegram_id,
                        student_was_not_polled_warning_template(student_info),
                    )

                    await delete_student_by_tg_id.execute(student_info.telegram_id)

            except Exception as e:
                notifier = container.get_dependency(BotNotifier)
                logger.info(student_info)
                try:
                    await delete_student_by_tg_id.execute(student_info.telegram_id)
                except:
                    logger.info("User already been deleted")

                await notifier.notify_about_job_exception(
                    e,
                    self.__class__.__name__,
                )
