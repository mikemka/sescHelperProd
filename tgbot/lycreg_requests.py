from __future__ import annotations

import datetime
import simplejson as json
import time

import aiohttp

import tgbot.errors as errors
from tgbot.redis_client import get_cache, set_cache
from tgbot.sesc_json import SESC_JSON


async def authorise_raw_request(
    client: aiohttp.ClientSession,
    captcha: str,
    captcha_id: str,
    user_login: str,
    user_password: str,
) -> str:
    async with client.post(
        SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil", "l":"{user_login}", "p":"{user_password}", "f":"login", '
             f'"ci":{captcha_id}, "c":{captcha} }}',
    ) as response:
        assert response.status == 200, 'Login-function response is not 200'
        return await response.text()


async def tabel_get_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"tabelGet","z":["{user_login}"]}}',
    ) as response:
        assert response.status == 200, 'tabelGet-function response is not 200'
        return await response.text()


async def subj_list_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"subjList"}}',
    ) as response:
        assert response.status == 200, 'subjList-function response is not 200'
        return await response.text()


async def teach_list_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"teachList"}}',
    ) as response:
        assert response.status == 200, 'teachList-function response is not 200'
        return await response.text()


async def journal_get_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"jrnGet","z":[]}}',
    ) as response:
        assert response.status == 200, 'jrnGet-function response is not 200'
        return await response.text()


async def lycreg_authorise(client: aiohttp.ClientSession, user_login: str, user_password: str) -> dict:
    captcha_bytes, captcha_id = await fetch_captcha(client=client)
    assert captcha_id is not None, "X-Cpt header doesn't exist"
    solved_captcha = await solve_captcha(captcha_bytes)
    authorise = await authorise_raw_request(
        client=client,
        captcha=solved_captcha,
        captcha_id=captcha_id,
        user_login=user_login,
        user_password=user_password,
    )
    if 'token' not in authorise:
        return {'error': errors.LYCREG.AUTH_ERROR}
    if '["pupil"]' not in authorise:
        return {'error': errors.LYCREG.ROLES_ERROR}
    return json.loads(authorise)


async def get_subj_list(
    client: aiohttp.ClientSession,
    user_login: str,
    user_token: str,
    no_cache: bool = False,
) -> dict:
    cache_key = f"subj_list:{user_login}"
    if not no_cache:
        cached = await get_cache(cache_key)
        if cached is not None:
            return SESC_JSON['default_subjects'] | cached
    result = json.loads(await subj_list_raw_request(client=client, user_login=user_login, user_token=user_token))
    await set_cache(cache_key, result, ttl=259200)  # 3 days
    return SESC_JSON['default_subjects'] | result


async def get_teach_list(
    client: aiohttp.ClientSession,
    user_login: str,
    user_token: str,
    no_cache: bool = False,
) -> dict:
    cache_key = f"teach_list:{user_login}"
    if not no_cache:
        cached = await get_cache(cache_key)
        if cached is not None:
            return cached
    raw = json.loads(await teach_list_raw_request(client=client, user_login=user_login, user_token=user_token))
    result = {i['login']: i['fio'] for i in raw}
    await set_cache(cache_key, result, ttl=259200)  # 3 days
    return result


async def get_week_days(week_shift: int = 0, no_cache: bool = False) -> tuple[list, str, str]:
    assert week_shift <= 0, 'week_shift must be <= 0'
    shift = -week_shift
    _now = datetime.datetime.now()
    today_str = _now.strftime('%Y-%m-%d')
    cache_key = f"week_days:{shift}:{today_str}"

    if not no_cache:
        cached = await get_cache(cache_key)
        if cached is not None:
            return cached[0], cached[1], cached[2]

    base = _now - datetime.timedelta(days=shift * 7)
    days = (
        [
            await date_convert((base - datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
            for i in range(1, base.weekday() + 1)
        ] + [
            await date_convert((base + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
            for i in range(7 - base.weekday())
        ]
    )
    week_start = (base - datetime.timedelta(days=base.weekday())).strftime('%d.%m.%Y')
    week_end = (base + datetime.timedelta(days=6 - base.weekday())).strftime('%d.%m.%Y')
    await set_cache(cache_key, [days, week_start, week_end], ttl=86400)
    return days, week_start, week_end


async def get_day(day_shift: int = 0) -> tuple[str, str]:
    _now = datetime.datetime.now()
    return (
        await date_convert((_now - datetime.timedelta(days=-day_shift - 1)).strftime('%Y-%m-%d')),
        (_now - datetime.timedelta(day_shift)).strftime('%d.%m.%Y'),
    )


async def fetch_captcha(client: aiohttp.ClientSession) -> tuple[bytes, int]:
    async with client.get(f'{SESC_JSON["scole_domain"]}cpt.a') as response:
        assert response.status == 200, '/cpt.a response status is not 200'
        return await response.read(), response.headers.get('X-Cpt')


async def solve_captcha(captcha_bytes: bytes) -> str:
    COLUMNS_PAIRS = {
        (524287, 458759): 0, (24579, 49155): 0, (7, 131071): 1, (415, 111): 1,
        (126983, 258079): 2, (24591, 57371): 2, (519935, 462343): 3, (115459, 99075): 3,
        (63503, 524287): 4, (227, 451): 4, (261951, 523903): 5, (24831, 6159): 5,
        (465927, 516095): 6, (15111, 29443): 6, (460799, 524287): 7, (24591, 12303): 7,
        (524287, 462343): 8, (27, 15): 8, (459207, 459143): 9, (57731, 49347): 9,
    }
    NUM2I = {
        0: 0, 1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6, 128: 7, 256: 8, 512: 9,
        1024: 10, 2048: 11, 4096: 12, 8192: 13, 16384: 14, 32768: 15, 65536: 16,
        131072: 17, 262144: 18, 524288: 19, 1048576: 20, 2097152: 21, 4194304: 22,
        8388608: 23, 16777216: 24, 33554432: 25, 67108864: 26, 134217728: 27,
        268435456: 28, 536870912: 29, 1073741824: 30, 2147483648: 31,
    }
    _data = captcha_bytes[104:-20]
    _numbers = (int(_data[i: 3630: 121].replace(b'\x00', b'0').replace(b'\x01', b'1'), 2) for i in range(121))
    _columns = [n >> NUM2I[n & -n] for n in _numbers]
    _solution, _wait_for_0 = '', False
    for i in range(120):
        _pair = _columns[i], _columns[i + 1]
        if _wait_for_0 and _pair[1] == 0:
            _wait_for_0 = False
        elif _pair in COLUMNS_PAIRS:
            _solution += str(COLUMNS_PAIRS[_pair])
            _wait_for_0 = True
    return _solution


async def date_convert(data_inp: str, full: int = 0) -> str:
    if '-' in data_inp:
        y, m, d, *_ = data_inp.split('-')
        m_num = int(m)
        m = m_num + (-9 if m_num > 8 else 3)
        return f'd{m}{d}'
    elif '.' in data_inp:
        d, m, *_ = data_inp.split('.')
        m_num = int(m)
        m = m_num + (-9 if m_num > 8 else 3)
        return f'd{m}{d}'
    else:
        m_num = int(data_inp[1])
        d = data_inp[2:4]
        m = f'{m_num + (9 if m_num < 4 else -3):0>2}'
        if full:
            date_obj = datetime.datetime.now()
            y = date_obj.year
            curr_m = date_obj.month
            if m_num < 4 and curr_m < 8:
                y -= 1
            return f'{y}-{m}-{d}'
        return f'{d}.{m}'


async def get_tabel(
    client: aiohttp.ClientSession,
    user_login: str,
    user_password: str,
    period: str = '',
) -> tuple[int, str]:
    def find_period_index(p):
        for j, k in enumerate(_ids):
            if k[0] == p:
                return j

    _auth = await lycreg_authorise(client=client, user_login=user_login, user_password=user_password)
    if _auth.get('error') is not None:
        return 1, _auth['error']
    _user_token = _auth['token']
    _tabel = await tabel_get_raw_request(client=client, user_login=user_login, user_token=_user_token)
    if _tabel in ('none', '{}'):
        return 1, errors.LYCREG.SERVER_ERROR
    _tabel = json.loads(_tabel)
    _ids = list(SESC_JSON.get('dtsit', {}).items())
    _render = ''
    if not period:
        period_set: set[str] = set()
        for _, _subj in _tabel.items():
            period_set.update(_subj.keys())
        period = max(period_set, key=find_period_index)
    _subject_codes = await get_subj_list(client=client, user_login=user_login, user_token=_user_token)
    for _subject_code, _marks in _tabel.items():
        if _subject_code not in _subject_codes:
            continue
        _mark = _marks.get(period, '-')
        _render += f'\n{_subject_codes[_subject_code]}: <i>{SESC_JSON["full_marks"].get(_mark, _mark)}</i>'
    return 0, f'<b>Табель</b> - {SESC_JSON["all_dtsit"][period][1]}\n{_render}'


async def get_grades(
    client: aiohttp.ClientSession,
    user_login: str,
    user_password: str,
    week_shift: int = 0,
) -> tuple[int, str]:
    _auth = await lycreg_authorise(client=client, user_login=user_login, user_password=user_password)
    if _auth.get('error') is not None:
        return 1, _auth['error']
    _user_token = _auth['token']

    _journal = await journal_get_raw_request(client=client, user_login=user_login, user_token=_user_token)
    if _journal == 'none':
        return 1, errors.LYCREG.NO_JOURNAL_ERROR
    _journal = json.loads(_journal)

    _teachers = await get_teach_list(client=client, user_login=user_login, user_token=_user_token)
    _subjects = await get_subj_list(client=client, user_login=user_login, user_token=_user_token)
    _current_weekday_code, _week_start, _week_end = await get_week_days(week_shift if week_shift <= 0 else 0)

    _render = ''
    for _subject_teacher, _lessons in _journal.items():
        _, _subject, _teacher_login, _marks = *_subject_teacher.split('_'), ''
        for _date_code, _lesson in _lessons.items():
            if _date_code not in _current_weekday_code:
                continue
            _, _, _weight, *_mark = _lesson
            if not _mark or not _mark[-1]:
                continue
            for _m in _mark[-1].split(' '):
                j = SESC_JSON["weights"][_weight]
                _marks += f'{_m}{(" (Вес: " + j + ")") if j else ""}, '
        if _marks:
            _render += f'\n\n<i>{_subjects.get(_subject)} - {_teachers.get(_teacher_login)}</i>\n<b>{_marks[:-2]}</b>'

    return 0, (
        f'<b>Оценки за неделю</b> <i>({_week_start} - {_week_end})</i>{_render}'
        if _render else
        f'{errors.LYCREG.NO_MARKS_BY_WEEK} <i>({_week_start} - {_week_end})</i>'
    )


async def get_homework(
    client: aiohttp.ClientSession,
    user_login: str,
    user_password: str,
    day_shift: int = 0,
) -> tuple[int, str]:
    _auth = await lycreg_authorise(client=client, user_login=user_login, user_password=user_password)
    if _auth.get('error') is not None:
        return 1, _auth['error']
    _user_token = _auth['token']

    _journal = await journal_get_raw_request(client=client, user_login=user_login, user_token=_user_token)
    if _journal == 'none':
        return 1, errors.LYCREG.NO_JOURNAL_ERROR
    _journal = json.loads(_journal)

    teachers = await get_teach_list(client=client, user_login=user_login, user_token=_user_token)
    subjects = await get_subj_list(client=client, user_login=user_login, user_token=_user_token)
    _day_code, _day = await get_day(day_shift)

    _render = ''
    for _subject_teacher, _lessons in _journal.items():
        _class, _subject, _teacher_login = _subject_teacher.split('_')
        _class_parts = _class.split('-')
        list_subject_name = (
            f'{subjects[_subject]}{"-" + _class_parts[1] if len(_class_parts) > 1 else ""}'
            if _subject in subjects
            else (_class_parts[1] if len(_class_parts) > 1 else teachers.get(_teacher_login))
        )
        x = '\n'.join([f'<code>{_lessons[i][1]}</code>' for i in _lessons if i == _day_code and _lessons[i][1]])
        if x:
            _render += f'<u>{list_subject_name}</u>\n{x}\n\n'

    return 0, (
        f'📙 <b>Домашнее задание</b> <i>({_day})</i>\n\n{_render}'
        if _render else
        f'{errors.LYCREG.NO_HOMETASK} <i>({_day})</i>'
    )
