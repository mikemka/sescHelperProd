from aiogram import executor
from dispatcher import dp
import handlers
from __init__ import user_status
from database import BotDB as DBActions
BotDB = DBActions('database.db')
from json_work import Json as JsonActions
Json = JsonActions()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
