import aiohttp
from aiogram import types
from dispatcher import dp
from transliterate import translit
from bot import user_status, Json, BotDB, user_password
from json_work import get_timetable_8ami, get_free_auditories
from aiogram.dispatcher.filters import Text
from . actions import *
import handlers.keyboards as keyboards
from filters import UserStatus
from fuzzywuzzy import fuzz
import handlers.lycreg


@dp.callback_query_handler(lambda c: c.data and c.data == 'start01')
async def process_callback_start01(message: types.CallbackQuery):
    if not BotDB.user_exists(message.from_user.id):
        user_status[message.from_user.id] = 'start > 01'
        await message.bot.send_message(message.from_user.id, 'Хорошо, теперь введите класс в формате "10А"',
                                       reply_markup=keyboards.get_forms_keyboard()); await message.answer()
    else: await message.answer(text='Вы уже зарегистрированы! Для начала воспользуйтесь /reg', show_alert=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('tabel'))
async def tabel_callback(cb: types.CallbackQuery):
    if user_password.get(cb.from_user.id):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
            _code, _text = await handlers.lycreg.get_tabel(
                client=_client,
                user_login=user_password[cb.from_user.id][0],
                user_password=user_password[cb.from_user.id][1],
                period=cb.data.split('*')[1],
            )
            if _code and _text.strip() != cb.message.html_text:
                await cb.bot.send_message(cb.from_user.id, _text, keyboards.try_again_tabel)
            elif _text.strip() != cb.message.html_text:
                await cb.message.edit_text(_text, reply_markup=keyboards.choose_tabel_period)
    else:
        await cb.bot.send_message(cb.from_user.id, 'Введите команду в формате: <code>/tabel [логин] [пароль]</code>')
    await cb.answer()


@dp.callback_query_handler(lambda c: c.data and c.data == 'start02')
async def process_callback_start02(message: types.CallbackQuery):
    user_status[message.from_user.id] = 'start > 02'
    await message.bot.send_message(message.from_user.id, '''
Хорошо, теперь введите свою фамилию и инициалы
Например, <b>Иванова Т А</b>
''', reply_markup=keyboards.get_teachers_keyboard())
    await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data == 'start03')
async def process_callback_start03(message: types.CallbackQuery): await start(message); await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data == 'start04')
async def process_callback_start04(message: types.CallbackQuery): await help_command(message); await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data == 'start05')
async def process_callback_start05(message: types.CallbackQuery): await call_schedule(message); await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data == 'start06')
async def process_callback_start06(message: types.CallbackQuery):
    if BotDB.user_exists(message.from_user.id):
        BotDB.remove_user(message.from_user.id)
        await message.bot.send_message(message.from_user.id, '''
<b>Приветствуем вас!</b>
Представьтесь, пожалуйста. Кто вы?
''', reply_markup=keyboards.StartButtons.keyboard); await message.answer()
    else: await start(message); await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('start'))
async def process_callback_kb6btn6(message: types.CallbackQuery): await message.answer('Ошибка!', show_alert=True)


@dp.message_handler(Text(equals='📅 Расписание'))
async def with_puree5(message: types.Message): await all_days(message)


@dp.message_handler(Text(equals='📅 Выбрать класс'))
async def with_puree5(message: types.Message): await thcom(message)


@dp.message_handler(Text(equals='📄 Все команды'))
async def with_puree6(message: types.Message): await help_command(message)


@dp.message_handler(Text(equals='На сегодня'))
async def with_puree7(message: types.Message): await today(message)


@dp.message_handler(Text(equals='На завтра'))
async def with_puree8(message: types.Message): await next_day(message)


@dp.message_handler(Text(contains='Статус текущего урока'))
async def with_puree9(message: types.Message): await lesson_status(message)


@dp.message_handler(Text(contains='8А-МИ'))
async def with_puree10(message: types.Message): await timetable_mi(message)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('help_'))
async def process_callback_kb5btn5(message: types.CallbackQuery):
    code = message.data[-2:]
    if code == '01':
        await all_days(message)
        await message.answer()
    elif code == '02':
        await today(message)
        await message.answer()
    elif code == '03':
        await next_day(message)
        await message.answer()
    elif code == '04':
        await lesson_status(message)
        await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('allco'))
async def process_callback_kb4btn4(message: types.CallbackQuery):
    if BotDB.user_exists(message.from_user.id):
        await message.bot.send_message(message.from_user.id, await Json.timetable(message.from_user.id, int(message.data[-1])))
        await message.answer()
    else:
        await message.answer(text='Вы не зарегистрированы!\nВоспользуйтесь /start', show_alert=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('allmi'))
async def process_callback_kb3btn3(message: types.CallbackQuery):
    await message.bot.send_message(message.from_user.id, await get_timetable_8ami(int(message.data[-1])))
    await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('allfr'))
async def process_callback_kb2btn2(message: types.CallbackQuery):
    if BotDB.user_exists(message.from_user.id):
        user_status[message.from_user.id] = '?free_date=' + message.data[-1]
        await message.bot.send_message(message.from_user.id, 'Выберите урок\nДля отмены воспользуйтесь /cancel', reply_markup=keyboards.lessons_buttons('lsnfr'))
        await message.answer()
    else: await message.answer(text='Вы не зарегистрированы!\nВоспользуйтесь /start', show_alert=True)


@dp.callback_query_handler(UserStatus('?free_date='), lambda c: c.data and c.data.startswith('lsnfr'))
async def process_callback_kb1btn1(message: types.CallbackQuery):
    await message.bot.send_message(message.from_user.id, await get_free_auditories(int(user_status[message.from_user.id][-1]), int(message.data[-1])))
    await message.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lsnfr'))
async def process_callback_kb1btn1(message: types.CallbackQuery):
    await message.answer(text='Ошибка! Воспользуйтесь /f', show_alert=True)


@dp.message_handler(UserStatus('start > 01'))
async def get_message(message: types.Message):
    tmp = translit(message.text.upper(), 'ru')
    if tmp in Json.data["group"]:
        BotDB.add_user(message.from_user.id, tmp)
        await message.bot.send_message(message.from_user.id, f"""
<b>Вы были успешно зарегистрированы</b>. Класс - {tmp}""", reply_markup=keyboards.HelpButton.keyboard)
        user_status.pop(message.from_user.id, None)
    else:
        await message.reply('Класс не найден! Попробуйте еще раз! Для отмены пропишите команду /cancel')


@dp.message_handler(UserStatus('thcom'))
async def get_message(message: types.Message):
    tmp = translit(message.text.upper(), 'ru')
    if tmp in Json.data["group"]:
        user_status[message.from_user.id] = f'thcom*{tmp}'
        await message.bot.send_message(message.from_user.id, f'Класс - {tmp}. Выберите день', reply_markup=keyboards.all_command_buttons('thcom'))
    else:
        await message.reply('Класс не найден! Попробуйте еще раз! Для отмены пропишите команду /cancel')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('thcom'))
async def process_callback_kb1btn1(message: types.CallbackQuery):
    if 'thcom*' in user_status[message.from_user.id]:
        if BotDB.user_exists(message.from_user.id):
            await message.bot.send_message(message.from_user.id, await Json.timetable(message.from_user.id, int(message.data[-1]), form=user_status[message.from_user.id][6:]), reply_markup=keyboards.keyboard_r())
            await message.answer()
        else:
            await message.answer(text='Вы не зарегистрированы!\nВоспользуйтесь /start', show_alert=True)
    else:
        await message.answer(text='Ошибка! Воспользуйтесь /th', show_alert=True)


@dp.message_handler(UserStatus('start > 02'))
async def get_message(message: types.Message):
    text, mc = translit(message.text, 'ru'), ('Нет', 0)
    for i in Json.data["teacher"]:
        if mc[1] < (k := fuzz.token_set_ratio(text, i)): mc = (i, k)
    user_status[message.from_user.id] = f'*i*{mc[0]}'
    await message.bot.send_message(message.from_user.id, f'Войти под аккаунтом <b>{mc[0]}</b>?',
                                   reply_markup=keyboards.YesNoButtons.keyboard)


@dp.callback_query_handler(lambda c: c.data == 'rt_yes01')
async def process_callback_rt_yes01(message: types.CallbackQuery):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_teacher(message.from_user.id, user_status[message.from_user.id][3:])
        await message.bot.send_message(message.from_user.id, '<b>Вы успешно вошли в систему!</b>',
                                       reply_markup=keyboards.HelpButton.keyboard); await message.answer()
    else: await message.answer(text='Произошла ошибка!\nВоспользуйтесь /start вновь', show_alert=True)


@dp.callback_query_handler(lambda c: c.data == 'rt_yes02')
async def process_callback_rt_yes02(message: types.CallbackQuery):
    user_status[message.from_user.id] = 'start > 02'
    await message.bot.send_message(message.from_user.id, '''<b>Попробуйте еще раз</b>
Для отмены операции пропишите /cancel'''); await message.answer()
