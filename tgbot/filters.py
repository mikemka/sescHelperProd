from aiogram import types
from aiogram.dispatcher.filters import Filter, BoundFilter
import config
from __init__ import user_status


class IsOwnerFilter(BoundFilter):
    key = "is_owner"

    async def check(self, message: types.Message):
        return message.from_user.id in config.ADMIN_IDS


class Timeout(Filter):
    key = "timeout"

    async def check(self, message: types.Message):
        return True


class UserStatus(BoundFilter):
    key = "check_by"

    def __init__(self, check_by):
        self.check_by = check_by

    async def check(self, message: types.Message):
        return self.check_by in user_status.setdefault(message.from_user.id, 'None')
