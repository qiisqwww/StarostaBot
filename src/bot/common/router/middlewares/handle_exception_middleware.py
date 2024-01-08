from typing import Any, Awaitable, Callable, TypeAlias

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from loguru import logger

EventType: TypeAlias = Message | CallbackQuery
HandlerType: TypeAlias = Callable[[EventType, dict[str, Any]], Awaitable[Any]]

__all__ = [
    "HandleExceptionMiddleware",
]


class HandleExceptionMiddleware(BaseMiddleware):
    async def __call__(self, handler: HandlerType, event: EventType, data: dict[str, Any]) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception(e)
            if isinstance(event, Message):
                return await event.answer(
                    "Что-то пошло не так, попробуйте снова или сообщите администраторам об ошибке в @noheadproblemsbot."
                )

            if event.message is None:
                return

            return await event.message.answer(
                "Что-то пошло не так, попробуйте снова или сообщите администраторам об ошибке в @noheadproblemsbot."
            )
