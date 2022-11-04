import aiogram.types
import aiohttp
import bot
import dispatcher
import handlers.keyboards as keyboards
import lycreg_requests


@dispatcher.dp.message_handler(commands=['lycreg'])
async def lycreg(message: aiogram.types.Message) -> None:
    _args = message.get_args().split()
    if len(_args) < 2:
        return await message.reply('Введите команду в формате: <code>/lycreg [логин] [пароль]</code>')
    _user_login, _user_password, *_ = _args
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
        auth = await lycreg_requests.lycreg_authorise(
            client=client,
            user_login=_user_login,
            user_password=_user_password,
        )
    await message.reply(f'<code>{auth}</code>', reply=False)


@dispatcher.dp.message_handler(commands=['tabel'])
async def tabel(message: aiogram.types.Message) -> None:
    _args = message.get_args().split()
    if len(_args) < 2:
        return await message.reply('Введите команду в формате: <code>/tabel [логин] [пароль]</code>')
    _user_login, _user_password, *_ = _args
    bot.user_password[message.from_user.id] = _user_login, _user_password
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
        _code, _text = await lycreg_requests.get_tabel(
            client=_client,
            user_login=_user_login,
            user_password=_user_password,
        )
        if _code:
            return await message.reply(_text, reply=False, reply_markup=keyboards.try_again_tabel)
        await message.reply(_text, reply=False, reply_markup=keyboards.choose_tabel_period)


@dispatcher.dp.message_handler(commands=['grades'])
async def grades(message: aiogram.types.Message) -> None:
    _args = message.get_args().split()
    if len(_args) < 2:
        return await message.reply('Введите команду в формате: <code>/grades [логин] [пароль]</code>')
    _user_login, _user_password, *_ = _args
    bot.user_password[message.from_user.id] = _user_login, _user_password
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
        _code, _text = await lycreg_requests.get_grades(
            client=_client,
            user_login=_user_login,
            user_password=_user_password,
        )
        if _code:
            return await message.reply(_text, reply=False, reply_markup=keyboards.try_again_grades)
        await message.reply(_text, reply=False, reply_markup=keyboards.grades_prev_next())
