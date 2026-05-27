from __future__ import annotations

import datetime

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from tgbot.sesc_json import SESC_JSON


# ── inline ────────────────────────────────────────────────────────────────────

start_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='🧑‍🎓 Я ученик', callback_data='start01'),
        InlineKeyboardButton(text='👩‍🏫 Я преподаватель', callback_data='start02'),
    ],
    [InlineKeyboardButton(text='🏫 СУНЦ УрФУ', url='https://lyceum.urfu.ru/')],
])

start_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='start03')],
])

start_buttons_registered = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📖 Помощь по командам', callback_data='start04')],
    [InlineKeyboardButton(text='Повторная регистрация', callback_data='start06')],
])

help_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📖 Помощь по командам', callback_data='start04')],
])

call_schedule_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🕒 Расписание звонков', callback_data='start05')],
    [InlineKeyboardButton(text='Официальный информер', url='https://lyceum.urfu.ru/informer')],
])

yes_no_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='✅ Да', callback_data='rt_yes01'),
        InlineKeyboardButton(text='❌ Нет', callback_data='rt_yes02'),
    ],
])

choose_tabel_period = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='1 четверть', callback_data='tabel*d205a'),
        InlineKeyboardButton(text='2 четверть', callback_data='tabel*d331b'),
    ],
    [
        InlineKeyboardButton(text='3 четверть', callback_data='tabel*d628d'),
        InlineKeyboardButton(text='4 четверть', callback_data='tabel*d915e'),
    ],
    [
        InlineKeyboardButton(text='1п', callback_data='tabel*d331c'),
        InlineKeyboardButton(text='2п', callback_data='tabel*d915f'),
        InlineKeyboardButton(text='Год', callback_data='tabel*d925g'),
    ],
])

try_again_tabel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Повторить попытку', callback_data='tabel*')],
])

try_again_grades = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Повторить попытку', callback_data='grades*')],
])

try_again_homework = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Повторить попытку', callback_data='homework*')],
])

how_we_use_password = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='Как мы используем ваш пароль?',
        url='https://telegra.ph/How-we-use-your-password-11-05',
    )],
])

lycreg_password_n_help = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='Как мы используем ваш пароль?',
        url='https://telegra.ph/How-we-use-your-password-11-05',
    )],
    [InlineKeyboardButton(text='📖 Помощь по командам', callback_data='start04')],
])

mailing_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='✅ Отправить всем', callback_data='mail_confirm'),
        InlineKeyboardButton(text='❌ Отмена', callback_data='mail_cancel'),
    ],
])


def grades_prev_next() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Текущая неделя', callback_data='grades*')],
        [
            InlineKeyboardButton(text='«', callback_data='grades*-1'),
            InlineKeyboardButton(text='»', callback_data='grades*1'),
        ],
    ])


def homework_prev_next() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сегодня', callback_data='homework*')],
        [
            InlineKeyboardButton(text='«', callback_data='homework*-1'),
            InlineKeyboardButton(text='»', callback_data='homework*1'),
        ],
    ])


def all_command_buttons(t: str = 'allco') -> InlineKeyboardMarkup:
    today = datetime.datetime.today().weekday() + 1
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📅 Сегодня', callback_data=f'{t}{today}')],
        [
            InlineKeyboardButton(text='Понедельник', callback_data=f'{t}1'),
            InlineKeyboardButton(text='Четверг', callback_data=f'{t}4'),
        ],
        [
            InlineKeyboardButton(text='Вторник', callback_data=f'{t}2'),
            InlineKeyboardButton(text='Пятница', callback_data=f'{t}5'),
        ],
        [
            InlineKeyboardButton(text='Среда', callback_data=f'{t}3'),
            InlineKeyboardButton(text='Суббота', callback_data=f'{t}6'),
        ],
    ])


def lessons_buttons(t: str = 'allsn') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='1 урок', callback_data=f'{t}0'),
            InlineKeyboardButton(text='2 урок', callback_data=f'{t}1'),
        ],
        [
            InlineKeyboardButton(text='3 урок', callback_data=f'{t}2'),
            InlineKeyboardButton(text='4 урок', callback_data=f'{t}3'),
        ],
        [
            InlineKeyboardButton(text='5 урок', callback_data=f'{t}4'),
            InlineKeyboardButton(text='6 урок', callback_data=f'{t}5'),
            InlineKeyboardButton(text='7 урок', callback_data=f'{t}6'),
        ],
    ])


# ── reply ─────────────────────────────────────────────────────────────────────

def keyboard_r(is_authorised: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text='📅 Расписание')],
        [
            KeyboardButton(text='На сегодня'),
            KeyboardButton(text='На завтра'),
            KeyboardButton(text='🕒 Уроки'),
        ],
        [
            KeyboardButton(text='📄 Все команды'),
            KeyboardButton(text='📅 Другой класс'),
        ],
    ]
    if is_authorised:
        rows.append([
            KeyboardButton(text='📖 Оценки'),
            KeyboardButton(text='📙 Задания'),
            KeyboardButton(text='📝 Табель'),
        ])
    else:
        rows.append([KeyboardButton(text='🔒 Вход')])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def get_forms_keyboard() -> ReplyKeyboardMarkup:
    forms = list(SESC_JSON['group'].keys())
    rows = [[KeyboardButton(text=f)] for f in forms]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)


def get_teachers_keyboard() -> ReplyKeyboardMarkup:
    teachers = list(SESC_JSON['teacher'].keys())
    rows = []
    for i in range(0, len(teachers), 2):
        row = [KeyboardButton(text=teachers[i])]
        if i + 1 < len(teachers):
            row.append(KeyboardButton(text=teachers[i + 1]))
        rows.append(row)
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)
