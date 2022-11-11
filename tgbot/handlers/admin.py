import aiogram.types
import aiohttp
import bot
import dispatcher
import filters
import handlers.keyboards as keyboards
import time
import lycreg_requests


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['admin'])
async def admin_help(message: aiogram.types.Message) -> None:
    await message.answer(
        '<b>Панель администратора</b>\n'
        '\n'
        '/count_users - Количество зарегистрированных пользователей\n'
        '/get_database - Скачать базу данных в формате .sqlite3\n'
        '/update_cache - Обновление кэша Scole\n'
        '/test_mail <code>[текст сообщения, поддерживается html]</code> - Проверка отображения сообщения\n'
        '<code>/mail [текст сообщения, поддерживается html]</code> - Массовая рассылка сообщений\n',
        # TODO: /unreg_user, /update_json
        reply_markup=keyboards.HelpButton.keyboard,
    )


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['mail'])
async def mail(message: aiogram.types.Message) -> None:
    _text, _users, _errors = message.text[6:], bot.BotDB.get_users(), 0
    for _user in _users:
        try:
            await message.bot.send_message(chat_id=_user[-1], text=_text)
        except:
            _errors += 1
    await message.answer(f'Отправлено {len(_users) - _errors} сообщения. {_errors} ошибок')


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['test_mail'])
async def test_mail(message: aiogram.types.Message) -> None:
    _text = message.text[11:]
    try:
        await message.answer(text=_text)
    except:
        return await message.answer(f'Отправлено 0 сообщения. 1 ошибок')
    await message.answer(f'Отправлено 1 сообщения. 0 ошибок')


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['count_users'])
async def count_users(message: aiogram.types.Message) -> None:
    await message.answer(f'Всего <b>{len(bot.BotDB.get_users())}</b> пользователей')


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['get_database'])
async def get_database(message: aiogram.types.Message) -> None:
    await message.reply_document(
        document=aiogram.types.InputFile('database.db', 'database.db'),
    )


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['update_cache'])
async def update_cache(message: aiogram.types.Message) -> None:
    _args = message.get_args().split()
    if len(_args) < 2:
        return await message.reply('Введите команду в формате: <code>/update_cache [логин] [пароль]</code>')
    _user_login, _user_password, *_ = _args
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
        _auth = await lycreg_requests.lycreg_authorise(
            client=client,
            user_login=_user_login,
            user_password=_user_password,
        )
        if _auth.get('error') is not None:
            return 1, _auth['error']
        _user_token = _auth['token']
        await lycreg_requests.get_subj_list(
            client=client,
            user_login=_user_login,
            user_token=_user_token,
            no_cache=True,
        )
        await lycreg_requests.get_teach_list(
            client=client,
            user_login=_user_login,
            user_token=_user_token,
            no_cache=True,
        )
        for i in range(5):
            await lycreg_requests.get_week_days(
                week_shift=-i,
                no_cache=True,
            )
    await message.answer('Updated')


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['lycreg_captcha'])
async def lycreg_captcha(message: aiogram.types.Message) -> None:
    fetch_time = time.time()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
        captcha, _ = await lycreg_requests.fetch_captcha(client)
    fetch_time = time.time() - fetch_time
    solve_time = time.time()
    cpt_content = await lycreg_requests.solve_captcha(captcha)
    await message.answer(
        f'<b>{cpt_content}</b>\n'
        f'<code>request={fetch_time * 1000 :.2f}ms\n'
        f'solving={(time.time() - solve_time) * 1000:.2f}ms</code>'
    )
