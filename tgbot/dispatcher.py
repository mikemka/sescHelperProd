import logging
from aiogram import Bot, Dispatcher
from filters import *
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# get token
if os.path.exists(dotenv_path := os.path.join(os.path.dirname(__file__), '.env')):
    load_dotenv(dotenv_path)

# init
bot = Bot(token=(os.environ['TOKEN'] if not os.environ.get('DEBUG') else os.environ['DEBUG_TOKEN']), parse_mode="HTML")
dp = Dispatcher(bot)

dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(Timeout)
dp.filters_factory.bind(UserStatus)
