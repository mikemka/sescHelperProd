from aiogram.dispatcher.filters import Text
import aiogram.types
import bot
import datetime
import dispatcher
import errors
import handlers.keyboards as keyboards
from bot import user_password


@dispatcher.dp.message_handler(commands=["start", "reg"])
async def start(message: aiogram.types.Message):
    if not bot.BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(
            message.from_user.id,
            '<b>Приветствуем вас!</b>\n'
            'Представьтесь, пожалуйста. Кто вы?',
            reply_markup=keyboards.StartButtons.keyboard,
        )
    await message.bot.send_message(
        message.from_user.id,
        errors.ALREADY_REGISTERED,
        reply_markup=keyboards.StartButtons1.keyboard,
    )


@dispatcher.dp.message_handler(commands='cancel')
async def cancel(message: aiogram.types.Message):
    bot.user_status.pop(message.from_user.id, None)
    await message.bot.send_message(message.from_user.id, 'Вы остановили выполнение операции')


@dispatcher.dp.message_handler(commands="mi")
async def timetable_mi(message: aiogram.types.Message):
    await message.bot.send_message(
        message.from_user.id,
        'Выберите день недели',
        reply_markup=keyboards.all_command_buttons('allmi'),
    )


@dispatcher.dp.message_handler(commands="help")
async def help_command(message: aiogram.types.Message):
    if bot.BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(
            message.from_user.id,
            '<i>📆 расписание</i>\n'
            '/today - Расписание на сегодня\n'
            '/next - Расписание на завтра\n'
            '/all - Расписание на любой день\n'
            '/status - Статус текущего урока\n'
            '/th - Расписание другого класса\n'
            '/call - Расписание звонков\n'
            '/free - Поиск свободного кабинета\n'
            '\n'
            '<i>📔 журнал</i>\n'
            '/lycreg - Сохранение пароля\n'
            '/tabel - Четвертные оценки\n'
            '/grades - Текущие оценки\n'
            '/homework - Домашние задания\n'
            '\n'
            '<i>🛠 сервис</i>\n'
            '/help - Вызвать данное меню\n'
            '/cancel - Прервать операцию\n'
            '/reg - Повторная регистрация\n'
            '/exit - Удалить аккаунт',
            reply_markup=keyboards.keyboard_r(is_autorised=message.from_user.id in user_password),
        )
    await message.bot.send_message(
        message.from_user.id,
        errors.SHOULD_REGISTER,
        reply_markup=keyboards.StartButton.keyboard,
    )


@dispatcher.dp.message_handler(commands="status")
async def lesson_status(message: aiogram.types.Message):
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
    
    if not bot.BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)
    current_time = datetime.datetime.today().minute + datetime.datetime.today().hour * 60
    e = '<b>Уроки уже закончились</b>'
    if current_time <= 915:
        for k, start_lesson in enumerate(
            (540, 580, 590, 630, 645, 685, 700, 740, 755, 795, 815, 855, 875, 915),
            start=1,
        ):
            if 915 >= current_time < start_lesson:
                if k % 2:
                    e = f'До начала {k // 2 + 1} урока {convert_time(start_lesson-current_time)}'
                else:
                    e = (
                        f'<b>Сейчас идет {k // 2} урок</b>\n'
                        f'До конца урока {convert_time(start_lesson - current_time)}'
                    )
                break
    if datetime.datetime.today().weekday() == 6:
        e = errors.NO_LESSONS
    await message.bot.send_message(message.from_user.id, e, reply_markup=keyboards.CallScheduleButton.keyboard)


@dispatcher.dp.message_handler(commands=["today", "t"])
async def today(message: aiogram.types.Message):
    if bot.BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(
            message.from_user.id,
            await bot.Json.timetable(message.from_user.id, 0),
        )
    await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dispatcher.dp.message_handler(commands=["next", "n"])
async def next_day(message: aiogram.types.Message):
    if bot.BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(
            message.from_user.id,
            await bot.Json.timetable(message.from_user.id, -1),
        )
    await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)


@dispatcher.dp.message_handler(commands=["all", "a"])
async def all_days(message: aiogram.types.Message):
    if not bot.BotDB.user_exists(message.from_user.id):
        return await message.bot.send_message(message.from_user.id, errors.SHOULD_REGISTER)
    await message.bot.send_message(
        message.from_user.id,
        'Выберите день недели',
        reply_markup=keyboards.all_command_buttons(),
    )


@dispatcher.dp.message_handler(commands=["call", "c"])
async def call_schedule(message: aiogram.types.Message):
    return await message.bot.send_message(
        message.from_user.id,
        '<b>Расписание звонков</b>\n'
        '\n'
        '<code>1</code>┃ <code>9:00   9:40</code>\n'
        '<code>2</code>┃ <code>9:50   10:30</code>\n'
        '<code>3</code>┃ <code>10:45  11:25</code>\n'
        '<code>4</code>┃ <code>11:40  12:20</code>\n'
        '<code>5</code>┃ <code>12:35  13:15</code>\n'
        '<code>6</code>┃ <code>13:35  14:15</code>\n'
        '<code>7</code>┃ <code>14:35  15:15</code>'
    )


@dispatcher.dp.message_handler(commands="exit")
async def unreg(message: aiogram.types.Message):
    if bot.BotDB.user_exists(message.from_user.id):
        bot.BotDB.remove_user(message.from_user.id)
        return await message.bot.send_message(
            message.from_user.id,
            'Ваш аккаунт был удален! Вы можете зарегистрироваться вновь',
            reply_markup=keyboards.StartButton.keyboard,
        )
    await message.bot.send_message(
        message.from_user.id,
        errors.SHOULD_REGISTER,
        reply_markup=keyboards.StartButton.keyboard,
    )


@dispatcher.dp.message_handler(commands=["free", "f"])
async def free_auditories(message: aiogram.types.Message):
    await message.bot.send_message(
        message.from_user.id,
        'Выберите день недели',
        reply_markup=keyboards.all_command_buttons('allfr'),
    )


@dispatcher.dp.message_handler(commands=["th"])
async def thcom(message: aiogram.types.Message):
    if bot.BotDB.user_exists(message.from_user.id):
        bot.user_status[message.from_user.id] = 'thcom'
        return await message.bot.send_message(
            message.from_user.id,
            'Выберите класс',
            reply_markup=keyboards.get_forms_keyboard(),
        )
    await message.bot.send_message(
        message.from_user.id,
        errors.SHOULD_REGISTER,
        reply_markup=keyboards.StartButton.keyboard,
    )
