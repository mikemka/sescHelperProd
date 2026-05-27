from __future__ import annotations

import datetime
import string

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import tgbot.errors as errors
import tgbot.lycreg_requests as lycreg_requests
from tgbot.db.models import UserCredentials
from tgbot.handlers import keyboards

router = Router(name=__name__)


async def _get_creds(tg_id: int):
    cred = await UserCredentials.get_or_none(tg_id=tg_id)
    if cred:
        return cred.lycreg_login, cred.lycreg_password
    return None


# ── callbacks ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('tabel'))
async def tabel_callback(cb: CallbackQuery) -> None:
    creds = await _get_creds(cb.from_user.id)
    if not creds:
        await cb.message.answer(errors.LYCREG.NO_PASSWORD)
        await cb.answer()
        return
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        code, text = await lycreg_requests.get_tabel(
            client=client,
            user_login=creds[0],
            user_password=creds[1],
            period=cb.data.split('*')[1],
        )
        if code and text.strip() != cb.message.html_text:
            await cb.message.answer(text, reply_markup=keyboards.try_again_tabel)
        elif text.strip() != cb.message.html_text:
            await cb.message.edit_text(text, reply_markup=keyboards.choose_tabel_period)
    await cb.answer()


@router.callback_query(F.data.startswith('grades'))
async def grades_callback(cb: CallbackQuery) -> None:
    creds = await _get_creds(cb.from_user.id)
    if not creds:
        await cb.message.answer(errors.LYCREG.NO_PASSWORD)
        await cb.answer()
        return
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        goal_week, shift = cb.data.split('*')[-1], 0
        if goal_week:
            text = cb.message.html_text
            i = text.find('(') + 1
            current = text[i:i + 11].split('.')[::-1]
            delta = datetime.timedelta(days=7)
            goal = datetime.datetime(*map(int, current)) + (delta if goal_week == '1' else -delta)
            shift = (datetime.datetime.now() - goal).days // 7
        code, text = await lycreg_requests.get_grades(
            client=client,
            user_login=creds[0],
            user_password=creds[1],
            week_shift=-shift,
        )
        if code and text.strip() != cb.message.html_text:
            await cb.message.answer(text, reply_markup=keyboards.try_again_grades)
        elif text.strip() != cb.message.html_text:
            await cb.message.edit_text(text, reply_markup=keyboards.grades_prev_next())
    await cb.answer()


@router.callback_query(F.data.startswith('homework'))
async def homework_callback(cb: CallbackQuery) -> None:
    creds = await _get_creds(cb.from_user.id)
    if not creds:
        await cb.message.answer(errors.LYCREG.NO_PASSWORD)
        await cb.answer()
        return
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        goal_day, shift = cb.data.split('*')[-1], 0
        if goal_day:
            text = cb.message.html_text
            i = text.find('(') + 1
            current = datetime.datetime(*map(int, text[i:i + 10].split('.')[::-1]))
            goal = current + datetime.timedelta(days=1) * int(goal_day)
            shift = (datetime.datetime.now() - goal).days
        code, text = await lycreg_requests.get_homework(
            client=client,
            user_login=creds[0],
            user_password=creds[1],
            day_shift=shift,
        )
        if code and text.strip() != cb.message.html_text:
            await cb.message.answer(text, reply_markup=keyboards.try_again_homework)
        elif text.strip() != cb.message.html_text:
            await cb.message.edit_text(text, reply_markup=keyboards.homework_prev_next())
    await cb.answer()


# ── button aliases ─────────────────────────────────────────────────────────────

@router.message(F.text == '🔒 Вход')
async def lycreg_btn(message: Message) -> None:
    await lycreg(message, ignore_args=True)


@router.message(F.text == '📝 Табель')
async def tabel_btn(message: Message) -> None:
    await tabel(message)


@router.message(F.text == '📖 Оценки')
async def grades_btn(message: Message) -> None:
    await grades(message)


@router.message(F.text == '📙 Задания')
async def homework_btn(message: Message) -> None:
    await homework(message)


# ── commands ───────────────────────────────────────────────────────────────────

@router.message(Command('lycreg'))
async def lycreg(message: Message, ignore_args: bool = False) -> None:
    args = [] if ignore_args else (message.text or '').split()[1:]
    creds = await _get_creds(message.from_user.id)

    if len(args) < 2:
        if creds:
            await message.answer(
                f'<b>Вы уже сохранили свой пароль</b> (<tg-spoiler>{"/".join(creds)}</tg-spoiler>)\n'
                '\n'
                'Для смены пароля, введите команду в формате: <code>/lycreg [логин] [пароль]</code>',
                reply_markup=keyboards.lycreg_password_n_help,
            )
            return
        await message.answer(
            '<b>Вход в электронный журнал «Шкала».</b>\n'
            '\n'
            'Введите команду в формате: <code>/lycreg [логин] [пароль]</code>',
            reply_markup=keyboards.how_we_use_password,
        )
        return

    user_login, user_pwd, *_ = args
    user_login = ''.join(c for c in user_login if c in string.ascii_letters or c in string.digits)
    user_pwd = ''.join(c for c in user_pwd if c in string.ascii_letters or c in string.digits)

    await UserCredentials.update_or_create(
        tg_id=message.from_user.id,
        defaults={'lycreg_login': user_login, 'lycreg_password': user_pwd},
    )
    await message.answer(
        '<b>Вы успешно сохранили пароль.</b> Мы сохраним ваши данные до следующей перезагрузки бота.\n'
        '\n'
        f'Логин: <tg-spoiler>{user_login}</tg-spoiler>,\n'
        f'Пароль: <tg-spoiler>{user_pwd}</tg-spoiler>.\n'
        '\n'
        'Для его смены, используйте команду /lycreg повторно.',
        reply_markup=keyboards.lycreg_password_n_help,
    )
    await message.delete()


@router.message(Command('tabel'))
async def tabel(message: Message) -> None:
    creds = await _get_creds(message.from_user.id)
    if not creds:
        await message.answer(errors.LYCREG.NO_PASSWORD)
        return
    msg = await message.answer(errors.LYCREG.PROCESS)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        code, text = await lycreg_requests.get_tabel(
            client=client, user_login=creds[0], user_password=creds[1],
        )
    if not code:
        await msg.edit_text(text, reply_markup=keyboards.choose_tabel_period)
        return
    # retry once
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        code, text = await lycreg_requests.get_tabel(
            client=client, user_login=creds[0], user_password=creds[1],
        )
    markup = keyboards.choose_tabel_period if not code else keyboards.try_again_tabel
    await msg.edit_text(text, reply_markup=markup)


@router.message(Command('grades'))
async def grades(message: Message) -> None:
    creds = await _get_creds(message.from_user.id)
    if not creds:
        await message.answer(errors.LYCREG.NO_PASSWORD)
        return
    msg = await message.answer(errors.LYCREG.PROCESS)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        code, text = await lycreg_requests.get_grades(
            client=client, user_login=creds[0], user_password=creds[1],
        )
    markup = keyboards.grades_prev_next() if not code else keyboards.try_again_grades
    await msg.edit_text(text, reply_markup=markup)


@router.message(Command('homework'))
async def homework(message: Message) -> None:
    creds = await _get_creds(message.from_user.id)
    if not creds:
        await message.answer(errors.LYCREG.NO_PASSWORD)
        return
    msg = await message.answer(errors.LYCREG.PROCESS)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        code, text = await lycreg_requests.get_homework(
            client=client, user_login=creds[0], user_password=creds[1],
        )
    markup = keyboards.homework_prev_next() if not code else keyboards.try_again_homework
    await msg.edit_text(text, reply_markup=markup)
