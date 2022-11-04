import datetime
import aiogram.types
import sesc_json


class StartButtons:
    keyboard = aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('🧑‍🎓 Я ученик', callback_data='start01'),
        aiogram.types.InlineKeyboardButton('👩‍🏫 Я преподаватель', callback_data='start02'),
    ).add(
        aiogram.types.InlineKeyboardButton('🏫 СУНЦ УрФУ', url='https://lyceum.urfu.ru/'),
    )


class StartButton:
    keyboard = aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('Зарегистрироваться', callback_data='start03'),
    )


class StartButtons1:
    keyboard = aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('📖 Помощь по командам', callback_data='start04'),
    ).add(
        aiogram.types.InlineKeyboardButton('Повторная регистрация', callback_data='start06'),
    )


class HelpButton:
    keyboard = aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('📖 Помощь по командам', callback_data='start04'),
    )


class CallScheduleButton:
    keyboard = aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('🕒 Расписание звонков', callback_data='start05'),
    ).add(
        aiogram.types.InlineKeyboardButton('Официальный информер', url='https://lyceum.urfu.ru/informer'),
    )


def keyboard_r():
    return aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        aiogram.types.KeyboardButton('📅 Расписание'),
    ).add(
        aiogram.types.KeyboardButton('На сегодня'),
        aiogram.types.KeyboardButton('На завтра'),
        aiogram.types.KeyboardButton('8А-МИ'),
    ).add(
        aiogram.types.KeyboardButton('🕒 Статус текущего урока'),
    ).add(
        aiogram.types.KeyboardButton('📄 Все команды'),
        aiogram.types.KeyboardButton('📅 Выбрать класс'),
    )


def all_command_buttons(t='allco'):
    return aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton(
            '📅 Сегодня', callback_data=f'{t}{datetime.datetime.today().weekday() + 1}',
        ),
    ).add(
        aiogram.types.InlineKeyboardButton('Понедельник', callback_data=f'{t}1'),
        aiogram.types.InlineKeyboardButton('Четверг', callback_data=f'{t}4'),
    ).add(
        aiogram.types.InlineKeyboardButton('Вторник', callback_data=f'{t}2'),
        aiogram.types.InlineKeyboardButton('Пятница', callback_data=f'{t}5'),
    ).add(
        aiogram.types.InlineKeyboardButton('Среда', callback_data=f'{t}3'),
        aiogram.types.InlineKeyboardButton('Суббота', callback_data=f'{t}6'),
    )


def lessons_buttons(t='allsn'):
    return aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('1 урок', callback_data=f'{t}0'),
        aiogram.types.InlineKeyboardButton('2 урок', callback_data=f'{t}1'),
    ).add(
        aiogram.types.InlineKeyboardButton('3 урок', callback_data=f'{t}2'),
        aiogram.types.InlineKeyboardButton('4 урок', callback_data=f'{t}3'),
    ).add(
        aiogram.types.InlineKeyboardButton('5 урок', callback_data=f'{t}4'),
        aiogram.types.InlineKeyboardButton('6 урок', callback_data=f'{t}5'),
        aiogram.types.InlineKeyboardButton('7 урок', callback_data=f'{t}6'),
    )


class YesNoButtons:
    keyboard = aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('✅ Да', callback_data='rt_yes01'),
        aiogram.types.InlineKeyboardButton('❌ Нет', callback_data='rt_yes02'),
    )


def get_forms_keyboard():
    #! FIXME
    json = sesc_json.SESC_JSON['group']
    e, k = 'aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(', 1
    for i in json:
        e += f"aiogram.types.KeyboardButton('{i}'),"
        k += 1
    return eval(f'{e})')


def get_teachers_keyboard():
    #! FIXME
    json = sesc_json.SESC_JSON['teacher']
    e, k = 'aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(', 1
    for i in json:
        e += f"aiogram.types.KeyboardButton('{i}'),"
        if k % 2 == 0: e += ').add('
        k += 1
    return eval(f'{e})')

choose_tabel_period = aiogram.types.InlineKeyboardMarkup().add(
    aiogram.types.InlineKeyboardButton('1 четверть', callback_data='tabel*d205a'),
    aiogram.types.InlineKeyboardButton('2 четверть', callback_data='tabel*d331b'),
).add(
    aiogram.types.InlineKeyboardButton('3 четверть', callback_data='tabel*d628d'),
    aiogram.types.InlineKeyboardButton('4 четверть', callback_data='tabel*d915e'),
).add(
    aiogram.types.InlineKeyboardButton('1п', callback_data='tabel*d331c'),
    aiogram.types.InlineKeyboardButton('2п', callback_data='tabel*d915f'),
    aiogram.types.InlineKeyboardButton('Год', callback_data='tabel*d925g'),
)

try_again_tabel = aiogram.types.InlineKeyboardMarkup().add(
    aiogram.types.InlineKeyboardButton('Повторить попытку', callback_data='tabel*'),
)

try_again_grades = aiogram.types.InlineKeyboardMarkup().add(
    aiogram.types.InlineKeyboardButton('Повторить попытку', callback_data='grades*'),
)


def grades_prev_next(prev_hidden=False, next_hidden=False):
    if prev_hidden:
        return aiogram.types.InlineKeyboardMarkup().add(
            aiogram.types.InlineKeyboardButton('→', callback_data='grades*1'),
        )
    elif next_hidden:
        return aiogram.types.InlineKeyboardMarkup().add(
            aiogram.types.InlineKeyboardButton('←', callback_data='grades*-1'),
        )
    return aiogram.types.InlineKeyboardMarkup().add(
        aiogram.types.InlineKeyboardButton('←', callback_data='grades*-1'),
        aiogram.types.InlineKeyboardButton('→', callback_data='grades*1'),
    )
