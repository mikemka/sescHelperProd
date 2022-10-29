import aiogram
import config
import filters
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialise bot & dispatcher
bot = aiogram.Bot(token=(config.TOKEN), parse_mode='HTML')
dp = aiogram.Dispatcher(bot)

# Load filters
dp.filters_factory.bind(filters.IsOwnerFilter)
dp.filters_factory.bind(filters.Timeout)
dp.filters_factory.bind(filters.UserStatus)
