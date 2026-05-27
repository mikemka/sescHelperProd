from __future__ import annotations

import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

import tgbot.errors as errors
from tgbot.db.models import User, UserCredentials
from tgbot.filters import UserStatusFilter
from tgbot.handlers import keyboards
from tgbot.redis_client import del_user_status, get_user_status, set_user_status

router = Router(name=__name__)


@router.message(Command('start', 'reg'))
async def start(message: Message, user_id: int | None = None) -> None:
    uid = user_id or message.from_user.id
    exists = await User.filter(tg_id=uid).exists()
    if not exists:
        await message.answer(
            '<b>Приветствуем вас!</b>\n'
            'Представьтесь, пожалуйста. Кто вы?',
            reply_markup=keyboards.start_buttons,
        )
        return
    await message.answer(errors.ALREADY_REGISTERED, reply_markup=keyboards.start_buttons_registered)


@router.message(Command('cancel'))
async def cancel(message: Message) -> None:
    await del_user_status(message.from_user.id)
    await message.answer('Вы остановили выполнение операции')


@router.message(Command('mi'))
async def timetable_mi(message: Message) -> None:
    await message.answer('Выберите день недели', reply_markup=keyboards.all_command_buttons('allmi'))


@router.message(Command('help'))
async def help_command(message: Message, user_id: int | None = None) -> None:
    uid = user_id or message.from_user.id
    if not await User.filter(tg_id=uid).exists():
        await message.answer(errors.SHOULD_REGISTER, reply_markup=keyboards.start_button)
        return
    cred = await UserCredentials.get_or_none(tg_id=uid)
    await message.answer(
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
        reply_markup=keyboards.keyboard_r(is_authorised=cred is not None),
    )


@router.message(Command('status'))
async def lesson_status(message: Message, user_id: int | None = None) -> None:
    def convert_minutes(m: int) -> str:
        if 10 < m < 20:
            return f'{m} минут'
        d = m % 10
        if d == 1:
            return f'{m} минута'
        elif 2 <= d <= 4:
            return f'{m} минуты'
        return f'{m} минут'

    def convert_hours(h: int) -> str:
        if 10 < h < 20:
            return f'{h} часов'
        d = h % 10
        if d == 1:
            return f'{h} час'
        elif 2 <= d <= 4:
            return f'{h} часа'
        return f'{h} часов'

    def convert_time(t: int) -> str:
        if t < 60:
            return convert_minutes(t)
        mins = t % 60
        if not mins:
            return convert_hours(t // 60)
        return f'{convert_hours(t // 60)} {convert_minutes(mins)}'

    if not await User.filter(tg_id=user_id or message.from_user.id).exists():
        await message.answer(errors.SHOULD_REGISTER)
        return

    current_time = datetime.datetime.today().minute + datetime.datetime.today().hour * 60
    e = '<b>Уроки уже закончились</b>'
    if current_time <= 915:
        for k, start_lesson in enumerate(
            (540, 580, 590, 630, 645, 685, 700, 740, 755, 795, 815, 855, 875, 915),
            start=1,
        ):
            if 915 >= current_time < start_lesson:
                if k % 2:
                    e = f'До начала {k // 2 + 1} урока {convert_time(start_lesson - current_time)}'
                else:
                    e = (
                        f'<b>Сейчас идет {k // 2} урок</b>\n'
                        f'До конца урока {convert_time(start_lesson - current_time)}'
                    )
                break
    if datetime.datetime.today().weekday() == 6:
        e = errors.NO_LESSONS
    await message.answer(e, reply_markup=keyboards.call_schedule_button)


@router.message(Command('today', 't'))
async def today(message: Message, user_id: int | None = None) -> None:
    from tgbot.json_work import Json
    uid = user_id or message.from_user.id
    if not await User.filter(tg_id=uid).exists():
        await message.answer(errors.SHOULD_REGISTER)
        return
    await message.answer(await Json().timetable(uid, 0))


@router.message(Command('next', 'n'))
async def next_day(message: Message, user_id: int | None = None) -> None:
    from tgbot.json_work import Json
    uid = user_id or message.from_user.id
    if not await User.filter(tg_id=uid).exists():
        await message.answer(errors.SHOULD_REGISTER)
        return
    await message.answer(await Json().timetable(uid, -1))


@router.message(Command('all', 'a'))
async def all_days(message: Message, user_id: int | None = None) -> None:
    uid = user_id or message.from_user.id
    if not await User.filter(tg_id=uid).exists():
        await message.answer(errors.SHOULD_REGISTER)
        return
    await message.answer('Выберите день недели', reply_markup=keyboards.all_command_buttons())


@router.message(Command('call', 'c'))
async def call_schedule(message: Message) -> None:
    await message.answer(
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


@router.message(Command('exit'))
async def unreg(message: Message) -> None:
    if await User.filter(tg_id=message.from_user.id).exists():
        await User.filter(tg_id=message.from_user.id).delete()
        await message.answer(
            'Ваш аккаунт был удален! Вы можете зарегистрироваться вновь',
            reply_markup=keyboards.start_button,
        )
        return
    await message.answer(errors.SHOULD_REGISTER, reply_markup=keyboards.start_button)


@router.message(Command('free', 'f'))
async def free_auditories(message: Message) -> None:
    await message.answer('Выберите день недели', reply_markup=keyboards.all_command_buttons('allfr'))


@router.message(Command('th'))
async def thcom(message: Message) -> None:
    if not await User.filter(tg_id=message.from_user.id).exists():
        await message.answer(errors.SHOULD_REGISTER, reply_markup=keyboards.start_button)
        return
    await set_user_status(message.from_user.id, 'thcom')
    await message.answer('Выберите класс', reply_markup=keyboards.get_forms_keyboard())


# ── text button aliases ────────────────────────────────────────────────────────

@router.message(F.text == '📅 Расписание')
async def btn_all_days(message: Message) -> None:
    await all_days(message)


@router.message(F.text == '📅 Выбрать класс')
async def btn_select_class(message: Message) -> None:
    await thcom(message)


@router.message(F.text == '📄 Все команды')
async def btn_all_commands(message: Message) -> None:
    await help_command(message)


@router.message(F.text == 'На сегодня')
async def btn_today(message: Message) -> None:
    await today(message)


@router.message(F.text == 'На завтра')
async def btn_next(message: Message) -> None:
    await next_day(message)


@router.message(F.text.contains('🕒 Уроки'))
async def btn_status(message: Message) -> None:
    await lesson_status(message)


@router.message(F.text.contains('8А-МИ'))
async def btn_mi(message: Message) -> None:
    await timetable_mi(message)


@router.message(F.text == '📅 Другой класс')
async def btn_other_class(message: Message) -> None:
    await thcom(message)


# ── user_status message handlers ──────────────────────────────────────────────

@router.message(UserStatusFilter('start > 01'))
async def register_student(message: Message) -> None:
    from transliterate import translit
    from tgbot.json_work import Json
    tmp = translit(message.text.upper(), 'ru')
    if tmp in Json().data["group"]:
        await User.create(
            tg_id=message.from_user.id,
            tg_username=message.from_user.username,
            tg_first_name=message.from_user.first_name,
            tg_last_name=message.from_user.last_name,
            form=tmp,
        )
        await del_user_status(message.from_user.id)
        await message.answer(
            f'<b>Вы были успешно зарегистрированы</b>. Класс - {tmp}',
            reply_markup=keyboards.help_button,
        )
    else:
        await message.reply('Класс не найден! Попробуйте еще раз! Для отмены пропишите команду /cancel')


@router.message(UserStatusFilter('thcom'))
async def thcom_class_input(message: Message) -> None:
    from transliterate import translit
    from tgbot.json_work import Json
    tmp = translit(message.text.upper(), 'ru')
    if tmp in Json().data["group"]:
        await set_user_status(message.from_user.id, f'thcom*{tmp}')
        await message.answer(
            f'Класс - {tmp}. Выберите день',
            reply_markup=keyboards.all_command_buttons('thcom'),
        )
    else:
        await message.reply('Класс не найден! Попробуйте еще раз! Для отмены пропишите команду /cancel')


@router.message(UserStatusFilter('start > 02'))
async def register_teacher(message: Message) -> None:
    from transliterate import translit
    from rapidfuzz import fuzz
    from tgbot.json_work import Json
    text, mc = translit(message.text, 'ru'), ('Нет', 0)
    for i in Json().data["teacher"]:
        if mc[1] < (k := fuzz.token_set_ratio(text, i)):
            mc = i, k
    await set_user_status(message.from_user.id, f'*i*{mc[0]}')
    await message.answer(f'Войти под аккаунтом <b>{mc[0]}</b>?', reply_markup=keyboards.yes_no_buttons)
