from aiogram.filters.callback_data import CallbackData

from src.enums import UniversityAlias

__all__ = [
    "UniversityCallbackData",
]


class UniversityCallbackData(CallbackData, prefix="handle_university"):  # type: ignore
    university_alias: UniversityAlias
