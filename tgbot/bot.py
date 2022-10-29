import aiogram
import config
import dispatcher
import handlers
from __init__ import user_status
from database import BotDB as DBActions
BotDB = DBActions(config.DATABASE_FILE_PATH)
from json_work import Json as JsonActions
Json = JsonActions()


if __name__ == "__main__":
    aiogram.executor.start_polling(dispatcher.dp, skip_updates=True)
