import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from sesc_json import SESC_JSON


class StartButtons:
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🧑‍🎓 Я ученик', callback_data='start01'),
        InlineKeyboardButton('👩‍🏫 Я преподаватель', callback_data='start02')
    ).add(InlineKeyboardButton('🏫 СУНЦ УрФУ', url='https://lyceum.urfu.ru/'))


class StartButton:
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Зарегистрироваться', callback_data='start03'))


class StartButtons1:
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('📖 Помощь по командам', callback_data='start04')).add(InlineKeyboardButton('Повторная регистрация', callback_data='start06'))


class HelpButton:
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('📖 Помощь по командам', callback_data='start04'))


class CallScheduleButton:
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('🕒 Расписание звонков', callback_data='start05')).add(InlineKeyboardButton('Официальный информер', url='https://lyceum.urfu.ru/informer'))


def keyboard_r():
    bt = (
        KeyboardButton('📅 Расписание'),
        KeyboardButton('На сегодня'),
        KeyboardButton('На завтра'),
        KeyboardButton('🕒 Статус текущего урока'),
        KeyboardButton('8А-МИ'),
        KeyboardButton('📄 Все команды'),
        KeyboardButton('📅 Выбрать класс'),
    )
    return ReplyKeyboardMarkup(resize_keyboard=True).add(bt[0]).add(bt[1], bt[2], bt[4]).add(bt[3]).add(bt[5], bt[6])


def all_command_buttons(t='allco'):
    return InlineKeyboardMarkup()\
        .add(InlineKeyboardButton('📅 Сегодня', callback_data=f'{t}{datetime.datetime.today().weekday() + 1}')) \
        .add(InlineKeyboardButton('Понедельник', callback_data=f'{t}1'),
             InlineKeyboardButton('Четверг', callback_data=f'{t}4')) \
        .add(InlineKeyboardButton('Вторник', callback_data=f'{t}2'),
             InlineKeyboardButton('Пятница', callback_data=f'{t}5')) \
        .add(InlineKeyboardButton('Среда', callback_data=f'{t}3'),
             InlineKeyboardButton('Суббота', callback_data=f'{t}6'))


def lessons_buttons(t='allsn'):
    return InlineKeyboardMarkup()\
        .add(InlineKeyboardButton('1 урок', callback_data=f'{t}0'),
             InlineKeyboardButton('2 урок', callback_data=f'{t}1')) \
        .add(InlineKeyboardButton('3 урок', callback_data=f'{t}2'),
             InlineKeyboardButton('4 урок', callback_data=f'{t}3')) \
        .add(InlineKeyboardButton('5 урок', callback_data=f'{t}4'),
             InlineKeyboardButton('6 урок', callback_data=f'{t}5'),
             InlineKeyboardButton('7 урок', callback_data=f'{t}6'))


class YesNoButtons:
    keyboard = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton('✅ Да', callback_data='rt_yes01'),
             InlineKeyboardButton('❌ Нет', callback_data='rt_yes02'))


def get_forms_keyboard():
    # ! FIXME
    json = SESC_JSON['group']
    e, k = 'ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(', 1
    for i in json:
        e += f"KeyboardButton('{i}'),"
        k += 1
    return eval(f'{e})')


def get_teachers_keyboard():
    json = SESC_JSON['teacher']
    e, k = 'ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(', 1
    for i in json:
        e += f"KeyboardButton('{i}'),"
        if k % 2 == 0: e += ').add('
        k += 1
    return eval(f'{e})')
