from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from tortoise import Tortoise

from tgbot.config import settings
from tgbot.db import TORTOISE_ORM
from tgbot.handlers import actions_router, admin_router, callbacks_router, lycreg_router
from tgbot.middlewares import LoggingMiddleware
from tgbot.redis_client import close_redis, init_redis

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
log = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    await init_redis()
    await Tortoise.init(config=TORTOISE_ORM)
    log.info('Bot started')


async def on_shutdown(bot: Bot) -> None:
    await Tortoise.close_connections()
    await close_redis()
    log.info('Bot stopped')


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # admin router first — filtered by ADMIN_GROUP_ID inside the router
    dp.include_router(admin_router)
    dp.include_router(callbacks_router)
    dp.include_router(lycreg_router)
    dp.include_router(actions_router)

    return dp


async def main() -> None:
    session = AiohttpSession(proxy=settings.PROXY) if settings.PROXY else None
    bot = Bot(
        token=settings.TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
