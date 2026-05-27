from __future__ import annotations

import csv
import io
import time

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from tgbot.config import settings
from tgbot.db.models import User
from tgbot.handlers.keyboards import mailing_keyboard
import tgbot.lycreg_requests as lycreg_requests
from tgbot.redis_client import set_cache, get_cache

router = Router(name=__name__)
router.message.filter(F.chat.id == settings.ADMIN_GROUP_ID)
router.callback_query.filter(F.message.chat.id == settings.ADMIN_GROUP_ID)


@router.message(Command('start', 'help', 'admin'))
async def admin_help(message: Message) -> None:
    await message.answer(
        '<i>🛠 админ-панель</i>\n'
        '\n'
        '/count_users — Количество зарегистрированных пользователей\n'
        '/users_ids — ID всех пользователей\n'
        '/users_full — Таблица информации о пользователях\n'
        '/stats — Статистика активных пользователей\n'
        '\n'
        '/id — ID чата и пользователя\n'
        '/mail — Рассылка\n'
        '/del_user — Удаление пользователя\n'
        '/block — Заблокировать пользователя\n'
        '/unblock — Разблокировать пользователя\n'
        '\n'
        '/lycreg_captcha — Проверка решения капчи\n'
        '/update_cache — Обновление кэша Scole\n',
    )


@router.message(Command('id'))
async def get_id(message: Message) -> None:
    await message.answer(
        f'Chat ID: <code>{message.chat.id}</code>\n'
        f'User ID: <code>{message.from_user.id}</code>'
    )


@router.message(Command('count_users'))
async def count_users(message: Message) -> None:
    await message.answer(f'Пользователей зарегистрировано: <b>{await User.all().count()}</b>')


@router.message(Command('users_ids', 'users_full'))
async def users_export(message: Message, command: CommandObject) -> None:
    users = await User.all().order_by('created_at')
    output = io.StringIO()
    writer = csv.writer(output)
    headers = (
        ['tg_id']
        if command.command == 'users_ids' else
        ['id', 'tg_id', 'tg_username', 'tg_first_name', 'tg_last_name', 'form', 'is_teacher', 'is_blocked', 'created_at']
    )
    writer.writerow(headers)
    for user in users:
        writer.writerow([getattr(user, attr) for attr in headers])
    csv_bytes = output.getvalue().encode('utf-8')
    output.close()
    await message.answer_document(
        document=BufferedInputFile(csv_bytes, filename=f'{command.command}.csv'),
    )


@router.message(Command('stats'))
async def stats(message: Message) -> None:
    from datetime import datetime, timedelta
    now = datetime.now()
    total = await User.all().count()
    blocked = await User.filter(is_blocked=True).count()
    new_today = await User.filter(created_at__gte=now.replace(hour=0, minute=0, second=0)).count()
    new_week = await User.filter(created_at__gte=now - timedelta(days=7)).count()
    dau = await User.filter(last_active_at__gte=now - timedelta(hours=24)).count()
    wau = await User.filter(last_active_at__gte=now - timedelta(days=7)).count()
    mau = await User.filter(last_active_at__gte=now - timedelta(days=30)).count()
    await message.answer(
        '<b>📊 Статистика пользователей</b>\n'
        '\n'
        '<i>👥 Пользователи</i>\n'
        f'Всего: <b>{total}</b>\n'
        f'Заблокировано: <b>{blocked}</b>\n'
        f'Новых сегодня: <b>{new_today}</b>\n'
        f'Новых за неделю: <b>{new_week}</b>\n'
        '\n'
        '<i>🟢 Активность</i>\n'
        f'За 24 часа (DAU): <b>{dau}</b>\n'
        f'За 7 дней (WAU): <b>{wau}</b>\n'
        f'За 30 дней (MAU): <b>{mau}</b>\n'
    )


@router.message(Command('del_user'))
async def del_user(message: Message, command: CommandObject) -> None:
    user_id = command.args
    if not user_id or not user_id.strip().isdigit():
        await message.answer('<code>/del_user [tg_id]</code>')
        return
    user = await User.get_or_none(tg_id=int(user_id.strip()))
    if user is None:
        await message.answer('Пользователь не найден')
        return
    await user.delete()
    await message.answer('Пользователь удален')


@router.message(Command('block'))
async def block_user(message: Message, command: CommandObject) -> None:
    user_id = command.args
    if not user_id or not user_id.strip().lstrip('-').isdigit():
        await message.answer('<code>/block [tg_id]</code>')
        return
    user = await User.get_or_none(tg_id=int(user_id.strip()))
    if user is None:
        await message.answer('Пользователь не найден')
        return
    user.is_blocked = True
    await user.save()
    name = user.tg_first_name or str(user.tg_id)
    await message.answer(f'🔒 Пользователь <b>{name}</b> (<code>{user.tg_id}</code>) заблокирован')


@router.message(Command('unblock'))
async def unblock_user(message: Message, command: CommandObject) -> None:
    user_id = command.args
    if not user_id or not user_id.strip().lstrip('-').isdigit():
        await message.answer('<code>/unblock [tg_id]</code>')
        return
    user = await User.get_or_none(tg_id=int(user_id.strip()))
    if user is None:
        await message.answer('Пользователь не найден')
        return
    user.is_blocked = False
    await user.save()
    name = user.tg_first_name or str(user.tg_id)
    await message.answer(f'🔓 Пользователь <b>{name}</b> (<code>{user.tg_id}</code>) разблокирован')


@router.message(Command('mail'))
async def mail_preview(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer('<code>/mail [текст рассылки (html разметка)]</code>')
        return
    text = command.args.strip()
    # store pending mail text in Redis (TTL 10 minutes)
    await set_cache('pending_mail', {'text': text}, ttl=600)
    try:
        await message.bot.send_message(
            chat_id=settings.ADMIN_GROUP_ID,
            text=f'<b>📢 Превью рассылки:</b>\n\n{text}',
            reply_markup=mailing_keyboard,
        )
    except Exception as e:
        await message.answer(f'Ошибка превью: <code>{e}</code>')


@router.callback_query(F.data == 'mail_confirm')
async def mail_confirm(cb: CallbackQuery) -> None:
    pending = await get_cache('pending_mail')
    if not pending:
        await cb.answer('Рассылка устарела или уже выполнена', show_alert=True)
        return

    text = pending['text']
    users = await User.filter(is_blocked=False).values_list('tg_id', flat=True)
    errors_count = 0
    for tg_id in users:
        try:
            await cb.bot.send_message(chat_id=tg_id, text=text)
        except Exception:
            errors_count += 1

    from tgbot.redis_client import get_redis
    await get_redis().delete('cache:pending_mail')

    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        f'✅ Отправлено: <b>{len(users) - errors_count}</b>\n'
        f'❌ Ошибок: <b>{errors_count}</b>'
    )
    await cb.answer()


@router.callback_query(F.data == 'mail_cancel')
async def mail_cancel(cb: CallbackQuery) -> None:
    from tgbot.redis_client import get_redis
    await get_redis().delete('cache:pending_mail')
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer('Рассылка отменена')
    await cb.answer()



@router.message(Command('lycreg_captcha'))
async def lycreg_captcha(message: Message) -> None:
    fetch_start = time.time()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        captcha, _ = await lycreg_requests.fetch_captcha(client)
    fetch_time = time.time() - fetch_start
    solve_start = time.time()
    cpt_content = await lycreg_requests.solve_captcha(captcha)
    await message.answer(
        f'<b>{cpt_content}</b>\n'
        f'<code>request={fetch_time * 1000:.2f}ms\n'
        f'solving={(time.time() - solve_start) * 1000:.2f}ms</code>'
    )


@router.message(Command('update_cache'))
async def update_cache(message: Message, command: CommandObject) -> None:
    args = (command.args or '').split()
    if len(args) < 2:
        await message.reply('Введите команду в формате: <code>/update_cache [логин] [пароль]</code>')
        return
    user_login, user_password, *_ = args
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        auth = await lycreg_requests.lycreg_authorise(
            client=client,
            user_login=user_login,
            user_password=user_password,
        )
        if auth.get('error') is not None:
            await message.reply(auth['error'])
            return
        user_token = auth['token']
        await lycreg_requests.get_subj_list(client=client, user_login=user_login, user_token=user_token, no_cache=True)
        await lycreg_requests.get_teach_list(client=client, user_login=user_login, user_token=user_token, no_cache=True)
        for i in range(5):
            await lycreg_requests.get_week_days(week_shift=-i, no_cache=True)
    await message.answer('✅ Кэш обновлён')


@router.message()
async def catch_all(message: Message) -> None:
    pass
