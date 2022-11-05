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
    await message.reply(
        '<b>Панель администратора</b>\n'
        '\n'
        '/count_users - Количество зарегистрированных пользователей\n'
        '/get_database - Скачать базу данных в формате .sqlite3\n'
        '/lycreg_captcha - Проверка работоспособности решения капчи\n'
        '/test_mail <code>[текст сообщения, поддерживается html]</code> - Проверка отображения сообщения\n'
        '<code>/mail [текст сообщения, поддерживается html]</code> - Массовая рассылка сообщений\n'
        '\n'
        'TODO: <code>/unreg_user</code>, <code>/update_json</code>',
        reply=False,
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
    await message.reply(f'Отправлено {len(_users) - _errors} сообщения. {_errors} ошибок', reply=False)


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['test_mail'])
async def test_mail(message: aiogram.types.Message) -> None:
    _text = message.text[11:]
    try:
        await message.reply(text=_text, reply=False)
    except:
        return await message.reply(f'Отправлено 0 сообщения. 1 ошибок', reply=False)
    await message.reply(f'Отправлено 1 сообщения. 0 ошибок', reply=False)


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['count_users'])
async def count_users(message: aiogram.types.Message) -> None:
    await message.reply(f'Всего <b>{len(bot.BotDB.get_users())}</b> пользователей', reply=False)


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['get_database'])
async def get_database(message: aiogram.types.Message) -> None:
    await message.reply_document(
        document=aiogram.types.InputFile('database.db', 'database.db'),
    )


@dispatcher.dp.message_handler(filters.IsOwnerFilter(), commands=['lycreg_captcha'])
async def lycreg_captcha(message: aiogram.types.Message) -> None:
    fetch_time = time.time()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
        cpt_file, _ = await lycreg_requests.fetch_captcha(client)
    fetch_time = time.time() - fetch_time
    captcha = cpt_file.read()
    solve_time = time.time()
    cpt_content = await lycreg_requests.solve_captcha(cpt_file)
    await message.reply_photo(
        photo=captcha,
        caption=f'<b>{cpt_content}</b>\n'
                f'<code>request={fetch_time * 1000 :.2f}ms\n'
                f'solving={(time.time() - solve_time) * 1000:.2f}ms</code>',
        reply=False,
    )
    cpt_file.close()
