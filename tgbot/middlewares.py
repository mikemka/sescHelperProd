from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from tgbot.db.models import UserLog


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            await UserLog.create(
                tg_id=event.from_user.id,
                tg_username=event.from_user.username,
                tg_first_name=event.from_user.first_name,
                log_type="message",
                text=event.text or event.caption,
            )
        elif isinstance(event, CallbackQuery) and event.from_user:
            await UserLog.create(
                tg_id=event.from_user.id,
                tg_username=event.from_user.username,
                tg_first_name=event.from_user.first_name,
                log_type="callback",
                text=event.data,
            )
        return await handler(event, data)
