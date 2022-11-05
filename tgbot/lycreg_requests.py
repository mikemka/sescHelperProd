import datetime
import aiohttp
import config
import errors
import PIL
import pyscreeze
import sesc_json
import simplejson as json
import tempfile
import time


async def authorise_raw_request(
    client: aiohttp.ClientSession,
    captcha: str,
    captcha_id: str,
    user_login: str,
    user_password: str
) -> str:
    async with client.post(
        sesc_json.SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil", "l":"{user_login}", "p":"{user_password}", "f":"login", '
             f'"ci":{captcha_id}, "c":{captcha} }}',
    ) as response:
        assert response.status == 200, 'Login-function response is not 200'
        return await response.text()


async def tabel_get_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        sesc_json.SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"tabelGet","z":["{user_login}"]}}',
    ) as response:
        assert response.status == 200, 'tabelGet-function response is not 200'
        return await response.text()


async def subj_list_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        sesc_json.SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"subjList"}}',
    ) as response:
        assert response.status == 200, 'subjList-function response is not 200'
        return await response.text()


async def teach_list_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        sesc_json.SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"teachList"}}',
    ) as response:
        assert response.status == 200, 'teachList-function response is not 200'
        return await response.text()


async def journal_get_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        sesc_json.SESC_JSON['scole_domain'],
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"jrnGet","z":[]}}',
    ) as response:
        assert response.status == 200, 'jrnGet-function response is not 200'
        return await response.text()


async def lycreg_authorise(client: aiohttp.ClientSession, user_login: str, user_password: str) -> dict:
    captcha_file, captcha_id = await fetch_captcha(client=client)
    assert captcha_id is not None, 'X-Cpt header doesn\'t exists'
    solved_captcha = await solve_captcha(captcha_file)
    captcha_file.close()
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


# cached
async def get_subj_list(client: aiohttp.ClientSession, user_login: str, user_token: str):
    # return cache
    _x = sesc_json.SESC_JSON.get('subject_list')
    if _x is not None and time.time() - sesc_json.SESC_JSON.get('^cache_subj_list', 0) < 259200:  # 3 days in seconds
        return sesc_json.SESC_JSON['default_subjects'] | _x
    # update cache
    sesc_json.SESC_JSON['^cache_subj_list'] = time.time()
    sesc_json.SESC_JSON['subject_list'] = json.loads(
        await subj_list_raw_request(client=client, user_login=user_login, user_token=user_token)
    )
    return sesc_json.SESC_JSON['default_subjects'] | sesc_json.SESC_JSON['subject_list']


# cached
async def get_teach_list(client: aiohttp.ClientSession, user_login: str, user_token: str):
    # return cache
    _x = sesc_json.SESC_JSON.get('teach_list')
    if _x is not None and time.time() - sesc_json.SESC_JSON.get('^cache_teach_list', 0) < 259200:  # 3 days in seconds
        return _x
    # update cache
    sesc_json.SESC_JSON['^cache_teach_list'] = time.time()
    sesc_json.SESC_JSON['teach_list'] = {
        i['login']: i['fio'] for i in json.loads(
            await teach_list_raw_request(client=client, user_login=user_login, user_token=user_token)
        )
    }
    return sesc_json.SESC_JSON['teach_list']


# cached
async def get_week_days(week_shift=0) -> tuple[list, str, str]:
    assert week_shift <= 0, 'week_shift must be <= 0'
    week_shift = -week_shift

    # return cache
    _x = sesc_json.SESC_JSON.get(f'current_week_days_{week_shift}')
    _cache_time = time.time() - sesc_json.SESC_JSON.get(f'^cache_week_days_{week_shift}', 0)
    if _x is not None and _cache_time < 10800:  # 3 hours in seconds
        return _x

    # update cache
    sesc_json.SESC_JSON[f'^cache_week_days_{week_shift}'] = time.time()
    _now = datetime.datetime.now() - datetime.timedelta(days=week_shift * 7)
    sesc_json.SESC_JSON[f'current_week_days_{week_shift}'] = (
        [
            await date_convert((_now - datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
            for i in range(1, _now.weekday() + 1)
        ] + [
            await date_convert((_now + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
            for i in range(7 - _now.weekday())
        ],
        (_now - datetime.timedelta(days=_now.weekday())).strftime('%d.%m.%Y'),
        (_now + datetime.timedelta(days=6 - _now.weekday())).strftime('%d.%m.%Y'),
    )
    return sesc_json.SESC_JSON[f'current_week_days_{week_shift}']


async def fetch_captcha(client: aiohttp.ClientSession) -> tuple[tempfile.TemporaryFile, int]:
    async with client.get(f'{sesc_json.SESC_JSON["scole_domain"]}cpt.a') as response:
        assert response.status == 200, '/cpt.a response status is not 200'
        file = tempfile.TemporaryFile(suffix='.png')
        file.write(await response.read())
        file.seek(0)
        return file, response.headers.get('X-Cpt')


async def solve_captcha(file: tempfile.TemporaryFile) -> str:
    captcha, results = PIL.Image.open(file).convert('RGBA'), []
    number_files = {config.BASE_DIR / 'numbers' / f'{i}_{j}.png': str(i) for i in range(10) for j in range(1, 3)}
    for file_name, number in number_files.items():
        number_image = PIL.Image.open(file_name)
        result = pyscreeze.locate(number_image, captcha, grayscale=True)
        while result is not None:
            result = (result[0], result[1], result[0] + result[2], result[1] + result[3])
            PIL.ImageDraw.Draw(captcha).rectangle(result, fill=0)
            results.append((number, result[0]))
            result = pyscreeze.locate(number_image, captcha, grayscale=True)
    results = [x[0] for x in sorted(results, key=lambda x: x[1])]
    return ''.join(results)


async def date_convert(data_inp: str, full=0) -> str:
    # translated to python from ini.js (scole)
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
        else:
            return f'{d}.{m}'


async def get_tabel(client: aiohttp.ClientSession, user_login: str, user_password: str, period='') -> tuple[int, str]:
    def x(i):
        for j, k in enumerate(_ids):
            if k[0] == i:
                return j
    
    _auth = await lycreg_authorise(
        client=client,
        user_login=user_login,
        user_password=user_password,
    )
    if _auth.get('error') is not None:
        return 1, _auth['error']
    _user_token = _auth['token']
    _tabel = await tabel_get_raw_request(
        client=client,
        user_login=user_login,
        user_token=_user_token,
    )
    if _tabel == 'none':
        return 1, errors.LYCREG.SERVER_ERROR
    if not len(_tabel):
        return 1, errors.LYCREG.NO_TABEL_ERROR
    _tabel, _ids, _render = json.loads(_tabel), sesc_json.SESC_JSON.get('dtsit').items(), ''
    if not period:
        period = set()
        for _, _subj in _tabel.items():
            period.update(_subj.keys())
        period = max(period, key=x)
    _subject_codes = await get_subj_list(
        client=client,
        user_login=user_login,
        user_token=_user_token,
    )
    for _subject_code, _marks in _tabel.items():
        if _subject_code not in _subject_codes:
            continue
        _mark = _marks.get(period, '-')
        _render += f'\n{_subject_codes[_subject_code]}: <i>{sesc_json.SESC_JSON["full_marks"].get(_mark, _mark)}</i>'
    return 0, f'<b>Табель</b> - {sesc_json.SESC_JSON["all_dtsit"][period][1]}\n{_render}'


async def get_grades(
    client: aiohttp.ClientSession,
    user_login: str,
    user_password: str,
    week_shift=0,
) -> tuple[int, str]:
    _auth = await lycreg_authorise(
        client=client,
        user_login=user_login,
        user_password=user_password,
    )
    if _auth.get('error') is not None:
        return 1, _auth['error']
    _user_token = _auth['token']

    _journal = await journal_get_raw_request(
        client=client,
        user_login=user_login,
        user_token=_user_token,
    )
    if _journal == 'none':
        return 1, errors.LYCREG.NO_JOURNAL_ERROR
    _journal = json.loads(_journal)

    _teachers = await get_teach_list(
        client=client,
        user_login=user_login,
        user_token=_user_token,
    )
    _subjects = await get_subj_list(
        client=client,
        user_login=user_login,
        user_token=_user_token,
    )
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
            for _mark in _mark[-1].split(' '):
                _marks += f'{_mark}{(" (Вес: " + j + ")") if (j := sesc_json.SESC_JSON["weights"][_weight]) else ""}, '
        if _marks:
            _render += f'\n\n<i>{_subjects.get(_subject)} - {_teachers.get(_teacher_login)}</i>\n<b>{_marks[:-2]}</b>'

    return 0, (
        f'<b>Оценки за неделю</b> <i>({_week_start} - {_week_end})</i>{_render}'
        if _render else f'{errors.LYCREG.NO_MARKS_BY_WEEK} <i>({_week_start} - {_week_end})</i>'
    )
