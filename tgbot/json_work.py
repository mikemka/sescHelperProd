import requests
import bs4
import json
from datetime import datetime
from bot import BotDB


class Json:
    # Инициализация json-файла
    def __init__(self):
        with open('data.json') as dataFile: self.data = json.load(dataFile)
        dataFile.close()

    # Преобразование информации и управление процессом создания таблицы
    def timetable(self, user_id: int, date: int, form=''):
        weekday = date % 7
        if not date:
            weekday = (datetime.today().weekday() + 1) % 7
        elif date == -1:
            weekday = (datetime.today().weekday() + 2) % 7
        if weekday:
            if form:
                return f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b> - {form}\n{"━" * 15}\n{self.create_table(self.get_json(weekday, self.data["group"][form]))}'
            if not BotDB.is_teacher(user_id):
                tmp = BotDB.get_user_form(user_id)
                user_form = self.data["group"][tmp]
                return f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b> - {tmp}\n{"━" * 15}\n{self.create_table(self.get_json(weekday, user_form))}'
            return f'<b>Расписание на {self.data["weekdays_inverted"][str(weekday)]}</b>\n{"━" * 15}\n{self.create_table(self.get_teacher_json(weekday, self.data["teacher"].setdefault(BotDB.get_user_form(user_id), 172)))}'
        return '<b>В этот день нет уроков!</b>'

    @staticmethod  # Отправление запроса учителя
    def get_teacher_json(weekday: int, teacher: str):
        return json.loads(requests.get('https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii', params={
            'type': '11', 'scheduleType': 'teacher', 'weekday': weekday, 'teacher': teacher}).text)

    @staticmethod  # Отправление запроса ученика
    def get_json(weekday: int, group: int):
        return json.loads(requests.get('https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii', params={
            'type': '11', 'scheduleType': 'group', 'weekday': weekday, 'group': group}).text)

    @staticmethod  # Создание таблицы
    def create_table(info: dict):
        def auditory_converter(s):
            if s == 'Нет': return ''
            elif (e := s.find('-')) == -1: return s
            else: return f'ин{s[e + 1:]}'
        ext, e_str = [['', '', ''] for _ in range(7)], [f'{i}┃ ' for i in range(1, 8)]
        for i in info['lessons']: ext[i["number"] - 1][i["subgroup"]] = f'{i["subject"][:10]}`{auditory_converter(i["auditory"][:8])}'
        for i in info['diffs']: ext[i["number"] - 1][i["subgroup"]] = f'<i>{i["subject"][:10]}`{auditory_converter(i["auditory"][:8])}</i>'
        for i in range(7):
            e_str[i] = f'{e_str[i]}{ext[i][1] if ext[i][1] else " ✕ "} ┃ {ext[i][2] if ext[i][2] else " ✕"}' \
                if ext[i][1] else f'<b>{e_str[i]}</b>{ext[i][0]}'
        return '\n'.join(e_str)


def get_weekday(_day: int):
    return ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")[_day % 6]


def get_timetable_8ami(date: int):
    def get_table():
        def get_info(html: str):
            tmp1 = html[html.find('Расписание уроков 8А (подгруппа МИ)'):html.rfind('<footer>')]
            tmp1 = tmp1[tmp1.find(weekday):]
            return tmp1[tmp1.find('<tbody>'):tmp1.find('</tbody>')]
        
        b = f"{bs4.BeautifulSoup(get_info(requests.get('https://lyceum.urfu.ru/8ami').text), features='html.parser').text}\t"
        ext, tmp, k = [f'{i}┃ ' for i in range(1, 8)], '', 0
        for i in b:
            if i == '\t':
                if tmp and tmp != '\t':
                    if k % 4 == 1: ext[k // 4] += tmp
                    elif k % 4 == 3: ext[k // 4] += f'`{tmp}'
                    k += 1
                tmp = ''
            elif i != '\n': tmp += i
        return '\n'.join([(i if i[3:] != 'нет`нет' else i[:2]) for i in ext])
    
    weekday, date = get_weekday(date - 1), date % 7
    return '<b>В этот день нет уроков!</b>' if not date else f'<b>{weekday}</b> - 8А-МИ\n{"━" * 15}\n{get_table()}'


def get_free_auditories(day: int, lesson: int):
    def get_table():
        ext = ''
        data = json.loads(requests.get('https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii', params={
            'type': '11', 'scheduleType': 'all', 'weekday': day}).text)['auditories']
        for aud in data:
            if not data[aud][lesson] and aud not in ('Нет', 'Библиотека', 'Общежитие') and 'ин' not in aud:
                ext += f'{aud} ┃ '
        return ext[:-3]
    
    lesson %= 7
    day %= 7
    return f'<b>Свободные аудитории</b>\n{get_weekday(day - 1)}, {lesson + 1} урок\n\n{get_table()}' if day else '<b>В этот день нет уроков!</b>'
