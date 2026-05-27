from __future__ import annotations

from typing import Union

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from tgbot.config import settings
from tgbot.redis_client import get_user_status


class IsAdminFilter(Filter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user.id in settings.ADMIN_IDS


class UserStatusFilter(Filter):
    def __init__(self, check_by: str) -> None:
        self.check_by = check_by

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        status = await get_user_status(event.from_user.id)
        return self.check_by in status
