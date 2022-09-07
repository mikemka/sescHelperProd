import aiohttp
import requests
import bs4
import simplejson as json
from datetime import datetime
from bot import BotDB
from sesc_json import SESC_JSON


class Json:
    # Инициализация json-файла
    def __init__(self):
        self.data = SESC_JSON

    # Преобразование информации и управление процессом создания таблицы
    def timetable(self, user_id: int, date: int, form=''):
        weekday = date % 7
        if not date:
            weekday = (datetime.today().weekday() + 1) % 7
        elif date == -1:
            weekday = (datetime.today().weekday() + 2) % 7
        if weekday:
            if form:
                return (
                    f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b> - {form}\n'
                    f'{"━" * 15}\n'
                    f'{self.create_table(self.get_json(weekday, self.data["group"][form]))}'
                )
            if BotDB.is_teacher(user_id):
                return (
                    f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b>\n'
                    f'{"━" * 15}\n'
                    f'{self.create_table(self.get_teacher_json(weekday, self.data["teacher"].setdefault(BotDB.get_user_form(user_id), 172)))}'
                )
            tmp = BotDB.get_user_form(user_id)
            user_form = self.data["group"][tmp]
            return (
                f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b> - {tmp}\n'
                f'{"━" * 15}\n'
                f'{self.create_table(self.get_json(weekday, user_form))}'
            )
        return '<b>В этот день нет уроков!</b>'

    @staticmethod  # Отправление запроса учителя
    def get_teacher_json(weekday: int, teacher: str):
        return json.loads(requests.get('https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii', params={
            'type': '11', 'scheduleType': 'teacher', 'weekday': weekday, 'teacher': teacher}).text)

    @staticmethod  # Отправление запроса ученика
    def get_json(weekday: int, group: int):
        return json.loads(requests.get('https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii', params={
            'type': '11', 'scheduleType': 'group', 'weekday': weekday, 'group': group}).text)

    @staticmethod
    async def get_json_v2(weekday: int, group: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii?type=11&scheduleType=group&{weekday=}&{group=}') as resp:
                return json.loads(await resp.text())

    @staticmethod  # Создание таблицы
    def create_table(info: dict):
        def auditory_converter(s: str):
            if s == 'Нет':
                return ''
            elif (e := s.find('-')) == -1:
                return s
            return f'ин{s[e + 1:]}'
        
        ext, e_str = [['', '', ''] for _ in range(7)], [f'{i}┃ ' for i in range(1, 8)]
        for lesson in info['lessons']:
            ext[lesson["number"] - 1][lesson["subgroup"]] = f'{lesson["subject"][:10]}`{auditory_converter(lesson["auditory"][:8])}'
        for lesson in info['diffs']:
            ext[lesson["number"] - 1][lesson["subgroup"]] = f'<i>{lesson["subject"][:10]}`{auditory_converter(lesson["auditory"][:8])}</i>'
            for unusued_subgroup in {0, 1, 2} - {lesson["subgroup"]}:
                ext[lesson["number"] - 1][unusued_subgroup] = ''
        for i in range(7):
            if ext[i][1]:
                e_str[i] = f'{e_str[i]}{ext[i][1] if ext[i][1] else " ✕ "} ┃ {ext[i][2] if ext[i][2] else " ✕"}'
            else:
                e_str[i] = f'<b>{e_str[i]}</b>{ext[i][0]}'
        return '\n'.join(e_str)


async def get_weekday(_day: int):
    return ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")[_day % 6]


async def get_timetable_8ami(date: int):
    async def get_table():
        async def get_info(html: str):
            tmp1 = html[html.find('Расписание уроков 8А (подгруппа МИ)'):html.rfind('<footer>')]
            tmp1 = tmp1[tmp1.find(weekday):]
            return tmp1[tmp1.find('<tbody>'):tmp1.find('</tbody>')]
        
        async with aiohttp.ClientSession() as session:
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
                        ext[k // 4] += f'`{tmp}'
                    k += 1
                tmp = ''
            elif i != '\n':
                tmp += i
        return '\n'.join([(i if i[3:] != 'нет`нет' else i[:2]) for i in ext])
    
    weekday, date = await get_weekday(date - 1), date % 7
    return '<b>В этот день нет уроков!</b>' if not date else f'<b>{weekday}</b> - 8А-МИ\n{"━" * 15}\n{await get_table()}'


async def get_free_auditories(weekday: int, lesson: int):
    async def get_table():
        ext = []
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii?type=11&scheduleType=all&{weekday=}') as resp:
                data = await resp.text()
                data = json.loads(data)['auditories']
                for aud in data:
                    if not data[aud][lesson] and aud not in ('Нет', 'Библиотека', 'Общежитие'):
                        ext += [aud]
        return ' ┃ '.join(ext)
    
    lesson %= 7
    weekday %= 7
    if not weekday:
        return '<b>В этот день нет уроков!</b>'
    return f'<b>Свободные аудитории</b>\n{await get_weekday(weekday - 1)}, {lesson + 1} урок\n\n{await get_table()}'
