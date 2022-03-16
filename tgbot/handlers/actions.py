from aiogram import types
from dispatcher import dp
from bot import BotDB, user_status, Json
from . import keyboards
from filters import Timeout
from datetime import datetime
import errors


@dp.message_handler(Timeout(), commands=["start", "reg"])
async def start(message: types.Message):
    if not BotDB.user_exists(message.from_user.id): await message.bot.send_message(message.from_user.id, '''
<b>Приветствуем вас!</b>
Представьтесь, пожалуйста. Кто вы?''', reply_markup=keyboards.StartButtons.keyboard)
    else: await message.bot.send_message(message.from_user.id, errors.ALREADY_REGISTERED,
                                         reply_markup=keyboards.StartButtons1.keyboard)


@dp.message_handler(Timeout(), commands='cancel')
async def cancel(message: types.Message):
    user_status.pop(message.from_user.id, None)
    await message.bot.send_message(message.from_user.id, 'Вы остановили выполнение операции')


@dp.message_handler(commands="mi")
async def timetable_mi(message: types.Message):
    await message.bot.send_message(message.from_user.id, 'Выберите день недели',
                                   reply_markup=keyboards.all_command_buttons('allmi'))


@dp.message_handler(Timeout(), commands="help")
async def help_command(message: types.Message):
    if BotDB.user_exists(message.from_user.id): await message.bot.send_message(message.from_user.id, '''
<b>Помощь по командам</b>

/today, /t - Расписание на сегодня
/next, /n - Расписание на завтра
/all, /a - Расписание на любой день
/status - Статус текущего урока
/th - <i>Расписание другого класса</i>
/call, /c - Расписание звонков
/free, /f - Свободные кабинеты

/cancel - Остановить выполнение операции
/reg - Повторная регистрация
/exit - Удалить аккаунт
''', reply_markup=keyboards.keyboard_r())
    else:
        await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER, reply_markup=keyboards.StartButton.keyboard)


@dp.message_handler(Timeout(), commands="status")
async def lesson_status(message: types.Message):
    """ Статус текущего урока """
    def convert_minutes(minutes):
        if 10 < minutes < 20: return f'{minutes} минут'
        else:
            last_digit = minutes % 10
            if last_digit == 1: return f'{minutes} минута'
            elif 2 <= last_digit <= 4: return f'{minutes} минуты'
            else: return f'{minutes} минут'

    def convert_hours(hours):
        if 10 < hours < 20: return f'{hours} часов'
        else:
            last_digit = hours % 10
            if last_digit == 1: return f'{hours} час'
            elif 2 <= last_digit <= 4: return f'{hours} часа'
            else: return f'{hours} часов'

    def convert_time(time):
        minutes = time % 60
        if time < 60: return convert_minutes(time)
        elif not minutes: return convert_hours(time // 60)
        else: return f'{convert_hours(time // 60)} {convert_minutes(minutes)}'

    if BotDB.user_exists(message.from_user.id):
        if datetime.today().weekday() != 6:
            current_time, e = datetime.today().minute + datetime.today().hour * 60, '<b>Уроки уже закончились</b>'
            if current_time <= 915:
                for k, start_lesson in enumerate((540, 580, 590, 630, 645, 685, 700, 740, 755, 795, 815, 855, 875, 915), start=1):
                    if 915 >= current_time < start_lesson:
                        e = f"<b>Сейчас идет {k//2} урок</b>\nДо конца урока {convert_time(start_lesson-current_time)}"\
                            if not k % 2 else f'До начала {k // 2 + 1} урока {convert_time(start_lesson-current_time)}'
                        break
            await message.bot.send_message(message.from_user.id, e, reply_markup=keyboards.CallScheduleButton.keyboard)
        else: await message.bot.send_message(message.from_user.id, errors.NO_LESSONS)
    else: await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dp.message_handler(Timeout(), commands=["today", "t"])
async def today(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        await message.bot.send_message(message.from_user.id, Json.timetable(message.from_user.id, 0))
    else: await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dp.message_handler(Timeout(), commands=["next", "n"])
async def next_day(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        await message.bot.send_message(message.from_user.id, Json.timetable(message.from_user.id, -1))
    else: await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dp.message_handler(Timeout(), commands=["all", "a"])
async def all_days(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        await message.bot.send_message(message.from_user.id, 'Выберите день недели',
                                       reply_markup=keyboards.all_command_buttons())
    else: await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dp.message_handler(Timeout(), commands=["call", "c"])
async def call_schedule(message: types.Message):
    if BotDB.user_exists(message.from_user.id): await message.bot.send_message(message.from_user.id, '''
<b>Расписание звонков</b>

1┃ 9:00    9:40
2┃ 9:50    10:30
3┃ 10:45  11:25
4┃ 11:40  12:20
5┃ 12:35  13:15
6┃ 13:35  14:15
7┃ 14:35  15:15''')
    else: await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dp.message_handler(Timeout(), commands="exit")
async def unreg(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        BotDB.remove_user(message.from_user.id)
        await message.bot.send_message(message.from_user.id, '''
Ваш аккаунт был удален! Вы можете зарегистрироваться вновь''', reply_markup=keyboards.StartButton.keyboard)
    else: await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER,
                                         reply_markup=keyboards.StartButton.keyboard)


@dp.message_handler(commands=["free", "f"])
async def free_auditories(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        await message.bot.send_message(message.from_user.id, 'Выберите день недели',
                                       reply_markup=keyboards.all_command_buttons('allfr'))
    else: await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER,
                                         reply_markup=keyboards.StartButton.keyboard)


@dp.message_handler(commands=["th"])
async def thcom(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        user_status[message.from_user.id] = 'thcom'
        await message.bot.send_message(message.from_user.id, 'Выберите класс', reply_markup=keyboards.get_forms_keyboard())
    else:
        await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER, reply_markup=keyboards.StartButton.keyboard)
