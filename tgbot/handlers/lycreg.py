import aiogram.dispatcher.filters as filters
import aiogram.types
import aiohttp
import bot
import datetime
import dispatcher
import errors
import handlers.keyboards as keyboards
import lycreg_requests
import string


@dispatcher.dp.callback_query_handler(filters.Text(startswith='tabel'))
async def tabel_callback(cb: aiogram.types.CallbackQuery):
    if bot.user_password.get(cb.from_user.id):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
            _code, _text = await lycreg_requests.get_tabel(
                client=_client,
                user_login=bot.user_password[cb.from_user.id][0],
                user_password=bot.user_password[cb.from_user.id][1],
                period=cb.data.split('*')[1],
            )
            if _code and _text.strip() != cb.message.html_text:
                await cb.bot.send_message(cb.from_user.id, _text, reply_markup=keyboards.try_again_tabel)
            elif _text.strip() != cb.message.html_text:
                await cb.message.edit_text(_text, reply_markup=keyboards.choose_tabel_period)
    else:
        await cb.bot.send_message(cb.from_user.id, errors.LYCREG.NO_PASSWORD)
    await cb.answer()


@dispatcher.dp.callback_query_handler(filters.Text(startswith='grades'))
async def grades_callback(cb: aiogram.types.CallbackQuery):
    # TODO: add hiding buttons
    if bot.user_password.get(cb.from_user.id):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
            _goal_week, _shift = cb.data.split('*')[-1], 0
            if _goal_week:
                _current = cb.message.html_text[(i := cb.message.html_text.find('(') + 1):i + 11].split('.')[::-1]
                _delta = datetime.timedelta(days=7)
                _goal = datetime.datetime(*map(int, _current)) + (_delta if _goal_week == '1' else -_delta)
                _shift = (datetime.datetime.now() - _goal).days // 7
            _code, _text = await lycreg_requests.get_grades(
                client=_client,
                user_login=bot.user_password[cb.from_user.id][0],
                user_password=bot.user_password[cb.from_user.id][1],
                week_shift=-_shift,
            )
            if _code and _text.strip() != cb.message.html_text:
                await cb.bot.send_message(cb.from_user.id, _text, reply_markup=keyboards.try_again_grades)
            elif _text.strip() != cb.message.html_text:
                await cb.message.edit_text(_text, reply_markup=keyboards.grades_prev_next())
    else:
        await cb.bot.send_message(cb.from_user.id, errors.LYCREG.NO_PASSWORD)
    await cb.answer()


@dispatcher.dp.callback_query_handler(filters.Text(startswith='homework'))
async def homework_callback(cb: aiogram.types.CallbackQuery):
    # TODO: add hiding buttons
    if bot.user_password.get(cb.from_user.id):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
            _goal_day, _shift = cb.data.split('*')[-1], 0
            if _goal_day:
                _current = datetime.datetime(*map(int, 
                    cb.message.html_text[(i := cb.message.html_text.find('(') + 1):i + 10].split('.')[::-1],
                ))
                _goal = _current + datetime.timedelta(days=1) * int(_goal_day)
                _shift = (datetime.datetime.now() - _goal).days
            _code, _text = await lycreg_requests.get_homework(
                client=_client,
                user_login=bot.user_password[cb.from_user.id][0],
                user_password=bot.user_password[cb.from_user.id][1],
                day_shift=_shift,
            )
            if _code and _text.strip() != cb.message.html_text:
                await cb.bot.send_message(cb.from_user.id, _text, reply_markup=keyboards.try_again_homework)
            elif _text.strip() != cb.message.html_text:
                await cb.message.edit_text(_text, reply_markup=keyboards.homework_prev_next())
    else:
        await cb.bot.send_message(cb.from_user.id, errors.LYCREG.NO_PASSWORD)
    await cb.answer()


@dispatcher.dp.message_handler(filters.Text(equals='🔒 Вход'))
async def lycreg_call(message: aiogram.types.Message):
    await lycreg(message, ignore_args=True)


@dispatcher.dp.message_handler(filters.Text(equals='📝 Табель'))
async def tabel_call(message: aiogram.types.Message):
    await tabel(message)


@dispatcher.dp.message_handler(filters.Text(equals='📖 Оценки'))
async def grades_call(message: aiogram.types.Message):
    await grades(message)


@dispatcher.dp.message_handler(filters.Text(equals='📙 Задания'))
async def homework_call(message: aiogram.types.Message):
    await homework(message)


@dispatcher.dp.message_handler(commands=['lycreg'])
async def lycreg(message: aiogram.types.Message, ignore_args=False) -> None:
    _args = []
    if not ignore_args:
        _args = message.get_args().split()
    _x = bot.user_password.get(message.from_user.id)
    if len(_args) < 2:
        if _x:
            return await message.answer(
                f'<b>Вы уже сохранили свой пароль</b> (<tg-spoiler>{"/".join(_x)}</tg-spoiler>)\n'
                '\n'
                'Для смены пароля, введите команду в формате: <code>/lycreg [логин] [пароль]</code>',
                reply_markup=keyboards.lycreg_password_n_help,
            )
        return await message.answer(
            '<b>Вход в электронный журнал «Шкала».</b>\n'
            '\n'
            'Введите команду в формате: <code>/lycreg [логин] [пароль]</code>',
            reply_markup=keyboards.how_we_use_password,
        )
    _user_login, _user_password, *_ = _args
    _user_login = ''.join((i for i in _user_login if i in string.ascii_letters or i in string.digits))
    _user_password = ''.join((i for i in _user_password if i in string.ascii_letters or i in string.digits))
    bot.user_password[message.from_user.id] = _user_login, _user_password
    await message.answer(
        '<b>Вы успешно сохранили пароль.</b> Мы сохраним ваши данные до следующей перезагрузки бота.\n'
        '\n'
        f'Логин: <tg-spoiler>{_user_login}</tg-spoiler>,\n'
        f'Пароль: <tg-spoiler>{_user_password}</tg-spoiler>.\n'
        '\n'
        'Для его смены, используйте команду /lycreg повторно.',
        reply_markup=keyboards.lycreg_password_n_help,
    )
    await message.delete()


@dispatcher.dp.message_handler(commands=['tabel'])
async def tabel(message: aiogram.types.Message) -> None:
    _x = bot.user_password.get(message.from_user.id)
    if not _x:
        return await message.answer(errors.LYCREG.NO_PASSWORD)
    _msg = await message.answer(errors.LYCREG.PROCESS)
    _user_login, _user_password = _x
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
        _code, _text = await lycreg_requests.get_tabel(
            client=_client,
            user_login=_user_login,
            user_password=_user_password,
        )
        if not _code:
            return await _msg.edit_text(_text, reply_markup=keyboards.choose_tabel_period)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
        _code, _text = await lycreg_requests.get_tabel(
            client=_client,
            user_login=_user_login,
            user_password=_user_password,
        )
        if not _code:
            return await _msg.edit_text(_text, reply_markup=keyboards.choose_tabel_period)
        await _msg.edit_text(_text, reply_markup=keyboards.try_again_tabel)


@dispatcher.dp.message_handler(commands=['grades'])
async def grades(message: aiogram.types.Message) -> None:
    _x = bot.user_password.get(message.from_user.id)
    if not _x:
        return await message.answer(errors.LYCREG.NO_PASSWORD)
    _msg = await message.answer(errors.LYCREG.PROCESS)
    _user_login, _user_password = _x
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
        _code, _text = await lycreg_requests.get_grades(
            client=_client,
            user_login=_user_login,
            user_password=_user_password,
        )
        if not _code:
            return await _msg.edit_text(_text, reply_markup=keyboards.grades_prev_next())
    await _msg.edit_text(_text, reply_markup=keyboards.try_again_grades)


@dispatcher.dp.message_handler(commands=['homework'])
async def homework(message: aiogram.types.Message) -> None:
    # homework command handler
    _x = bot.user_password.get(message.from_user.id)
    if not _x:
        return await message.answer(errors.LYCREG.NO_PASSWORD)
    _msg = await message.answer(errors.LYCREG.PROCESS)
    _user_login, _user_password = _x
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
        _code, _text = await lycreg_requests.get_homework(
            client=_client,
            user_login=_user_login,
            user_password=_user_password,
        )
        if not _code:
            return await _msg.edit_text(_text, reply_markup=keyboards.homework_prev_next())
    await _msg.edit_text(_text, reply_markup=keyboards.homework_prev_next())
