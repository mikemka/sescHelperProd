import aiogram
import config
import dispatcher
import handlers
from __init__ import user_status, user_password

from database import BotDB as DBActions
if not config.DATABASE_FILE_PATH.exists():
    BotDB = DBActions(config.DATABASE_FILE_PATH)
    BotDB.create_table_users()
else:
    BotDB = DBActions(config.DATABASE_FILE_PATH)

from json_work import Json as JsonActions
Json = JsonActions()


if __name__ == "__main__":
    # ping pseudo-unused imports
    handlers
    user_status
    user_password

    # start execution script
    aiogram.executor.start_polling(dispatcher.dp, skip_updates=True)
