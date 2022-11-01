import aiogram.types
import aiohttp
import bot
import dispatcher
import handlers.keyboards as keyboards
import lycreg_requests
import sesc_json


try:
    import simplejson as json
except ImportError:
    import json


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
async def tabel_get(message: aiogram.types.Message) -> None:
    _args = message.get_args().split()
    if len(_args) < 2:
        return await message.reply('Введите команду в формате: <code>/tabel [логин] [пароль]</code>')
    _user_login, _user_password, *_ = _args
    bot.user_password[message.from_user.id] = _user_login, _user_password
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as _client:
        _code, _text = await get_tabel(client=_client, user_login=_user_login, user_password=_user_password)
        if _code:
            return await message.reply(_text, reply=False, reply_markup=keyboards.try_again_tabel)
        await message.reply(_text, reply=False, reply_markup=keyboards.choose_tabel_period)


async def get_tabel(client: aiohttp.ClientSession, user_login: str, user_password: str, period='') -> tuple[int, str]:
    def x(i):
        for j, k in enumerate(_ids):
            if k[0] == i:
                return j
    
    _auth = await lycreg_requests.lycreg_authorise(
        client=client,
        user_login=user_login,
        user_password=user_password,
    )
    if _auth.get('error') is not None:
        return 1, _auth['error']
    _user_token = _auth.get('token')
    _tabel = await lycreg_requests.tabel_get_raw_request(
        client=client,
        user_login=user_login,
        user_token=_user_token,
    )
    if _tabel == 'none':
        return 1, 'Ошибка сервера. Не удалось выполнить запрос.'
    if not len(_tabel):
        return 1, '<b>Табель не сгенерирован.</b>\nНе выставлено ни одной отметки промежуточной аттестации.'
    _tabel, _ids, _render = json.loads(_tabel), sesc_json.SESC_JSON.get('dtsit').items(), ''
    if not period:
        period = set()
        for _, _subj in _tabel.items():
            period.update(_subj.keys())
        period = max(period, key=x)
    _subject_codes = await lycreg_requests.get_subj_list(
        client=client,
        user_login=user_login,
        user_token=_user_token,
    )
    for _subject_code, _marks in _tabel.items():
        if _subject_code not in _subject_codes:
            continue
        _mark = _marks.get(period, '-')
        _render += f'<b>{_subject_codes.get(_subject_code, 0)}</b>: {sesc_json.SESC_JSON["full_marks"].get(_mark, _mark)}\n'
    return (
        0,
        f'<b>Табель</b> - {(sesc_json.SESC_JSON["dtsit"] | sesc_json.SESC_JSON["add_dtsit"])[period][1]}\n\n{_render}'
    )
