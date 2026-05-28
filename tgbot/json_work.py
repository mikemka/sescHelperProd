from __future__ import annotations

import aiohttp
import bs4
import simplejson as json
from datetime import datetime

from tgbot.db.models import User
from tgbot.schedule_data import get_schedule_data
from tgbot.sesc_json import SESC_JSON


class Json:
    def __init__(self) -> None:
        self.data = SESC_JSON

    async def timetable(self, user_id: int, date: int, form: str = '') -> str:
        weekday = date % 7
        if not date:
            weekday = (datetime.today().weekday() + 1) % 7
        elif date == -1:
            weekday = (datetime.today().weekday() + 2) % 7

        if not weekday:
            return '<b>В этот день нет уроков!</b>'

        sched = await get_schedule_data()

        if form:
            return (
                f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b> - <code>{form}</code>\n'
                f'{"━" * 15}\n'
                f'{await self.create_table(await self.get_json(weekday, int(sched["group"][form])))}'
            )

        user = await User.get(tg_id=user_id)
        if user.is_teacher:
            teacher_id = int(sched["teacher"].get(user.form, 172))
            return (
                f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b>\n'
                f'{"━" * 15}\n'
                f'{await self.create_table(await self.get_teacher_json(weekday, teacher_id))}'
            )

        user_form_id = int(sched["group"][user.form])
        return (
            f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b> - <code>{user.form}</code>\n'
            f'{"━" * 15}\n'
            f'{await self.create_table(await self.get_json(weekday, user_form_id))}'
        )

    @staticmethod
    async def get_teacher_json(weekday: int, teacher: int) -> dict:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(
                f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii'
                f'?type=11&scheduleType=teacher&weekday={weekday}&teacher={teacher}'
            ) as resp:
                return json.loads(await resp.text())

    @staticmethod
    async def get_json(weekday: int, group: int) -> dict:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(
                f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii'
                f'?type=11&scheduleType=group&weekday={weekday}&group={group}'
            ) as resp:
                return json.loads(await resp.text())

    @staticmethod
    async def create_table(info: dict) -> str:
        def auditory_converter(s: str) -> str:
            if s == 'Нет':
                return ''
            e = s.find('-')
            return s if e == -1 else f'ин{s[e + 1:]}'

        ext = [['', '', ''] for _ in range(7)]
        e_str = ['' for _ in range(7)]

        for lesson in info['lessons']:
            ext[lesson["number"] - 1][lesson["subgroup"]] = (
                f'{lesson["subject"][:10]}`<code>{auditory_converter(lesson["auditory"][:8])}</code>'
            )
        for lesson in info['diffs']:
            if lesson["subgroup"] == 0:
                ext[lesson["number"] - 1][1] = ''
                ext[lesson["number"] - 1][2] = ''
            else:
                ext[lesson["number"] - 1][0] = ''
            ext[lesson["number"] - 1][lesson["subgroup"]] = (
                f'<i>{lesson["subject"][:10]}`</i><code>{auditory_converter(lesson["auditory"][:8])}</code>'
            )
        for i, lesson in enumerate(ext):
            if lesson[0]:
                e_str[i] = lesson[0]
            elif lesson[1] and lesson[2]:
                e_str[i] = f'{lesson[1]} ┃ {lesson[2]}'
            elif lesson[1]:
                e_str[i] = f'{lesson[1]} ┃ ✕'
            elif lesson[2]:
                e_str[i] = f' ✕ ┃ {lesson[2]}'

        return '\n'.join([f'<code>{i + 1}</code>┃ {lesson}' for i, lesson in enumerate(e_str)])


async def get_weekday(_day: int) -> str:
    return ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")[_day % 6]


async def get_timetable_8ami(date: int) -> str:
    async def get_table() -> str:
        async def get_info(html: str) -> str:
            tmp1 = html[html.find('Расписание уроков 8А (подгруппа МИ)'):html.rfind('<footer>')]
            tmp1 = tmp1[tmp1.find(weekday):]
            return tmp1[tmp1.find('<tbody>'):tmp1.find('</tbody>')]

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get('https://lyceum.urfu.ru/8ami') as resp:
                data = await resp.text()
                b = f"{bs4.BeautifulSoup(await get_info(data), features='html.parser').text}\t"

        ext, tmp, k = [f'{i}┃ ' for i in range(1, 8)], '', 0
        for i in b:
            if i == '\t':
                if tmp and tmp != '\t':
                    if k % 4 == 1:
                        ext[k // 4] += tmp
                    elif k % 4 == 3:
                        ext[k // 4] += f'`<code>{tmp}</code>'
                    k += 1
                tmp = ''
            elif i != '\n':
                tmp += i
        return '\n'.join([(i if i[3:] != 'нет`нет' else i[:2]) for i in ext])

    weekday, date = await get_weekday(date - 1), date % 7
    if not date:
        return '<b>В этот день нет уроков!</b>'
    return f'<b>{weekday}</b> - 8А-МИ\n{"━" * 15}\n{await get_table()}'


async def get_free_auditories(weekday: int, lesson: int) -> str:
    async def get_table() -> str:
        ext = []
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(
                f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii'
                f'?type=11&scheduleType=all&weekday={weekday}'
            ) as resp:
                data = json.loads(await resp.text())['auditories']
                for aud in data:
                    if not data[aud][lesson] and aud not in ('Нет', 'Библиотека', 'Общежитие'):
                        ext.append(aud)
        return ' ┃ '.join(ext)

    lesson %= 7
    weekday %= 7
    if not weekday:
        return '<b>В этот день нет уроков!</b>'
    return f'<b>Свободные аудитории</b>\n{await get_weekday(weekday - 1)}, {lesson + 1} урок\n\n{await get_table()}'
