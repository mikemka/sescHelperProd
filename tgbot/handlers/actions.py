from aiogram import types
from dispatcher import dp
from bot import BotDB, user_status, Json
from . import keyboards
from filters import Timeout, IsOwnerFilter
from datetime import datetime
import errors


@dp.message_handler(Timeout(), commands=["start", "reg"])
async def start(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(
            message.from_user.id,
            '<b>Приветствуем вас!</b>\n'
            'Представьтесь, пожалуйста. Кто вы?',
            reply_markup=keyboards.StartButtons.keyboard,
        )
    await message.bot.send_message(message.from_user.id, errors.ALREADY_REGISTERED, reply_markup=keyboards.StartButtons1.keyboard)


@dp.message_handler(Timeout(), commands='cancel')
async def cancel(message: types.Message):
    user_status.pop(message.from_user.id, None)
    await message.bot.send_message(message.from_user.id, 'Вы остановили выполнение операции')


@dp.message_handler(commands="mi")
async def timetable_mi(message: types.Message):
    await message.bot.send_message(message.from_user.id, 'Выберите день недели', reply_markup=keyboards.all_command_buttons('allmi'))


@dp.message_handler(Timeout(), commands="help")
async def help_command(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(
            message.from_user.id,
            '<b>Помощь по командам</b>\n'
            '\n'
            '/today, /t - Расписание на сегодня\n'
            '/next, /n - Расписание на завтра\n'
            '/all, /a - Расписание на любой день\n'
            '/status - Статус текущего урока\n'
            '/th - Расписание другого класса\n'
            '/call, /c - Расписание звонков\n'
            '/free, /f - Свободные кабинеты\n'
            '\n'
            '/help - Вызвать данное меню\n'
            '/cancel - Остановить выполнение операции\n'
            '/reg - Повторная регистрация\n'
            '/exit - Удалить аккаунт',
            reply_markup=keyboards.keyboard_r(),
        )
    await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER, reply_markup=keyboards.StartButton.keyboard)


@dp.message_handler(Timeout(), commands="status")
async def lesson_status(message: types.Message):
    """ Статус текущего урока """
    def convert_minutes(_minutes):
        if 10 < _minutes < 20:
            return f'{_minutes} минут'
        _last_digit = _minutes % 10
        if _last_digit == 1:
            return f'{_minutes} минута'
        elif 2 <= _last_digit <= 4:
            return f'{_minutes} минуты'
        return f'{_minutes} минут'

    def convert_hours(_hours):
        if 10 < _hours < 20:
            return f'{_hours} часов'
        _last_digit = _hours % 10
        if _last_digit == 1:
            return f'{_hours} час'
        elif 2 <= _last_digit <= 4:
            return f'{_hours} часа'
        return f'{_hours} часов'

    def convert_time(_time):
        if _time < 60:
            return convert_minutes(_time)
        if not (_minutes := _time % 60):
            return convert_hours(_time // 60)
        return f'{convert_hours(_time // 60)} {convert_minutes(_minutes)}'
    
    if not BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)
    if datetime.today().weekday() == 6:
        return await message.bot.send_message(message.from_user.id, errors.NO_LESSONS)
    current_time, e = datetime.today().minute + datetime.today().hour * 60, '<b>Уроки уже закончились</b>'
    if current_time <= 915:
        for k, start_lesson in enumerate((540, 580, 590, 630, 645, 685, 700, 740, 755, 795, 815, 855, 875, 915), start=1):
            if 915 >= current_time < start_lesson:
                e = f"<b>Сейчас идет {k//2} урок</b>\nДо конца урока {convert_time(start_lesson-current_time)}"\
                    if not k % 2 else f'До начала {k // 2 + 1} урока {convert_time(start_lesson-current_time)}'
                break
    await message.bot.send_message(message.from_user.id, e, reply_markup=keyboards.CallScheduleButton.keyboard)


@dp.message_handler(Timeout(), commands=["today", "t"])
async def today(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(message.from_user.id, Json.timetable(message.from_user.id, 0))
    await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dp.message_handler(Timeout(), commands=["next", "n"])
async def next_day(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(message.from_user.id, Json.timetable(message.from_user.id, -1))
    await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dp.message_handler(Timeout(), commands=["all", "a"])
async def all_days(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)
    await message.bot.send_message(message.from_user.id, 'Выберите день недели', reply_markup=keyboards.all_command_buttons())


@dp.message_handler(Timeout(), commands=["call", "c"])
async def call_schedule(message: types.Message):
    return await message.bot.send_message(
        message.from_user.id,
        '<b>Расписание звонков</b>\n'
        '\n'
        '<code>1┃ 9:00   9:40</code>\n'
        '<code>2┃ 9:50   10:30</code>\n'
        '<code>3┃ 10:45  11:25</code>\n'
        '<code>4┃ 11:40  12:20</code>\n'
        '<code>5┃ 12:35  13:15</code>\n'
        '<code>6┃ 13:35  14:15</code>\n'
        '<code>7┃ 14:35  15:15</code>',
    )


@dp.message_handler(Timeout(), commands="exit")
async def unreg(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        BotDB.remove_user(message.from_user.id)
        return await message.bot.send_message(
            message.from_user.id,
            'Ваш аккаунт был удален! Вы можете зарегистрироваться вновь',
            reply_markup=keyboards.StartButton.keyboard,
        )
    await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER, reply_markup=keyboards.StartButton.keyboard)


@dp.message_handler(commands=["free", "f"])
async def free_auditories(message: types.Message):
    await message.bot.send_message(message.from_user.id, 'Выберите день недели', reply_markup=keyboards.all_command_buttons('allfr'))


@dp.message_handler(commands=["th"])
async def thcom(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        user_status[message.from_user.id] = 'thcom'
        return await message.bot.send_message(message.from_user.id, 'Выберите класс', reply_markup=keyboards.get_forms_keyboard())
    await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER, reply_markup=keyboards.StartButton.keyboard,)


@dp.message_handler(IsOwnerFilter(), commands=['mail'])
async def mail(message: types.Message):
    _text, _users, _errors = message.text[6:], BotDB.get_users(), 0
    for _user in _users:
        try:
            await message.bot.send_message(chat_id=_user[-1], text=_text)
        except:
            _errors += 1
    await message.reply(f'Отправлено {len(_users) - _errors} сообщения. {_errors} ошибок', reply=False)


"""
TODO
@dp.message_handler(IsOwnerFilter(), commands=['unreg_user'])
async def unreg_user(message: types.Message):
    _text = message.text[12:]
    if not _text or not _text.isdigit():
        return await message.reply('/unreg_user [id юзера]', reply=False)
    _user_id = int(_text)
    print(_user_id)
    if not BotDB.user_exists(_user_id):
        return await message.reply('юзера с данным id не существует', reply=False)
    BotDB.remove_user(BotDB.get_user_id(_user_id))
    await message.reply('успешно удален', reply=False)
"""
