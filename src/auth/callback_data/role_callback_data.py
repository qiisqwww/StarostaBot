from aiogram.filters.callback_data import CallbackData

from src.enums import Role

__all__ = [
    "RoleCallbackData",
]


class RoleCallbackData(CallbackData, prefix="handle_role"):  # type: ignore
    role: Role
