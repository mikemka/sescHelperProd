from __future__ import annotations

import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery

import tgbot.errors as errors
from tgbot.db.models import User, UserCredentials
from tgbot.filters import UserStatusFilter
from tgbot.handlers import keyboards
from tgbot.json_work import Json, get_free_auditories, get_timetable_8ami
from tgbot.redis_client import (
    del_user_status,
    get_user_status,
    set_user_status,
)

router = Router(name=__name__)

_json = Json()


# ── registration callbacks ─────────────────────────────────────────────────────

@router.callback_query(F.data == 'start01')
async def cb_start01(cb: CallbackQuery) -> None:
    if await User.filter(tg_id=cb.from_user.id).exists():
        await cb.answer(text='Вы уже зарегистрированы! Для начала воспользуйтесь /reg', show_alert=True)
        return
    await set_user_status(cb.from_user.id, 'start > 01')
    await cb.message.answer('Хорошо, теперь введите класс в формате "10А"', reply_markup=keyboards.get_forms_keyboard())
    await cb.answer()


@router.callback_query(F.data == 'start02')
async def cb_start02(cb: CallbackQuery) -> None:
    await set_user_status(cb.from_user.id, 'start > 02')
    await cb.message.answer(
        'Хорошо, теперь введите свою фамилию и инициалы\nНапример, <b>Иванова Т А</b>',
        reply_markup=keyboards.get_teachers_keyboard(),
    )
    await cb.answer()


@router.callback_query(F.data == 'start03')
async def cb_start03(cb: CallbackQuery) -> None:
    from tgbot.handlers.actions import start
    await start(cb.message, user_id=cb.from_user.id)
    await cb.answer()


@router.callback_query(F.data == 'start04')
async def cb_start04(cb: CallbackQuery) -> None:
    from tgbot.handlers.actions import help_command
    await help_command(cb.message, user_id=cb.from_user.id)
    await cb.answer()


@router.callback_query(F.data == 'start05')
async def cb_start05(cb: CallbackQuery) -> None:
    from tgbot.handlers.actions import call_schedule
    await call_schedule(cb.message)
    await cb.answer()


@router.callback_query(F.data == 'start06')
async def cb_start06(cb: CallbackQuery) -> None:
    if await User.filter(tg_id=cb.from_user.id).exists():
        await User.filter(tg_id=cb.from_user.id).delete()
        await cb.message.answer(
            '<b>Приветствуем вас!</b>\nПредставьтесь, пожалуйста. Кто вы?',
            reply_markup=keyboards.start_buttons,
        )
        await cb.answer()
        return
    from tgbot.handlers.actions import start
    await start(cb.message, user_id=cb.from_user.id)
    await cb.answer()


@router.callback_query(F.data.startswith('start'))
async def cb_start_unknown(cb: CallbackQuery) -> None:
    await cb.answer('Ошибка!', show_alert=True)


# ── teacher confirmation ───────────────────────────────────────────────────────

@router.callback_query(F.data == 'rt_yes01')
async def cb_confirm_teacher(cb: CallbackQuery) -> None:
    if await User.filter(tg_id=cb.from_user.id).exists():
        await cb.answer(text='Произошла ошибка!\nВоспользуйтесь /start вновь', show_alert=True)
        return
    status = await get_user_status(cb.from_user.id)
    teacher_name = status[3:]
    await User.create(
        tg_id=cb.from_user.id,
        tg_username=cb.from_user.username,
        tg_first_name=cb.from_user.first_name,
        tg_last_name=cb.from_user.last_name,
        form=teacher_name,
        is_teacher=True,
    )
    await del_user_status(cb.from_user.id)
    await cb.message.answer('<b>Вы успешно вошли в систему!</b>', reply_markup=keyboards.help_button)
    await cb.answer()


@router.callback_query(F.data == 'rt_yes02')
async def cb_retry_teacher(cb: CallbackQuery) -> None:
    await set_user_status(cb.from_user.id, 'start > 02')
    await cb.message.answer('<b>Попробуйте еще раз</b>\nДля отмены операции пропишите /cancel')
    await cb.answer()


# ── help shortcuts ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('help_'))
async def cb_help(cb: CallbackQuery) -> None:
    from tgbot.handlers.actions import all_days, lesson_status, next_day, today
    code = cb.data[-2:]
    if code == '01':
        await all_days(cb.message, user_id=cb.from_user.id)
    elif code == '02':
        await today(cb.message, user_id=cb.from_user.id)
    elif code == '03':
        await next_day(cb.message, user_id=cb.from_user.id)
    elif code == '04':
        await lesson_status(cb.message, user_id=cb.from_user.id)
    await cb.answer()


# ── timetable callbacks ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('allco'))
async def cb_allco(cb: CallbackQuery) -> None:
    if not await User.filter(tg_id=cb.from_user.id).exists():
        await cb.answer(text='Вы не зарегистрированы!\nВоспользуйтесь /start', show_alert=True)
        return
    await cb.message.answer(await _json.timetable(cb.from_user.id, int(cb.data[-1])))
    await cb.answer()


@router.callback_query(F.data.startswith('allmi'))
async def cb_allmi(cb: CallbackQuery) -> None:
    await cb.message.answer(await get_timetable_8ami(int(cb.data[-1])))
    await cb.answer()


@router.callback_query(F.data.startswith('allfr'))
async def cb_allfr(cb: CallbackQuery) -> None:
    if not await User.filter(tg_id=cb.from_user.id).exists():
        await cb.answer(text='Вы не зарегистрированы!\nВоспользуйтесь /start', show_alert=True)
        return
    await set_user_status(cb.from_user.id, f'?free_date={cb.data[-1]}')
    await cb.message.answer(
        'Выберите урок\nДля отмены воспользуйтесь /cancel',
        reply_markup=keyboards.lessons_buttons('lsnfr'),
    )
    await cb.answer()


@router.callback_query(UserStatusFilter('?free_date='), F.data.startswith('lsnfr'))
async def cb_lsnfr_with_status(cb: CallbackQuery) -> None:
    status = await get_user_status(cb.from_user.id)
    await cb.message.answer(await get_free_auditories(int(status[-1]), int(cb.data[-1])))
    await cb.answer()


@router.callback_query(F.data.startswith('lsnfr'))
async def cb_lsnfr_no_status(cb: CallbackQuery) -> None:
    await cb.answer(text='Ошибка! Воспользуйтесь /f', show_alert=True)


# ── thcom callback ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('thcom'))
async def cb_thcom(cb: CallbackQuery) -> None:
    status = await get_user_status(cb.from_user.id)
    if 'thcom*' not in status:
        await cb.answer(text='Ошибка! Воспользуйтесь /th', show_alert=True)
        return
    if not await User.filter(tg_id=cb.from_user.id).exists():
        await cb.answer(text='Вы не зарегистрированы!\nВоспользуйтесь /start', show_alert=True)
        return
    cred = await UserCredentials.get_or_none(tg_id=cb.from_user.id)
    await cb.message.answer(
        await _json.timetable(cb.from_user.id, int(cb.data[-1]), form=status[6:]),
        reply_markup=keyboards.keyboard_r(is_authorised=cred is not None),
    )
    await cb.answer()
