import aiohttp
import config
import PIL
import pyscreeze
import sesc_json
import tempfile


try:
    import simplejson as json
except ImportError:
    import json


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
        return {'error': '<b>Логин / пароль / код неверны.</b>\n\n'
                            'Проверьте и измените их в случае необходимости с помощью команды /change.'}
    if '["pupil"]' not in authorise:
        return {'error': '<b>Бот не может работать с правами выше ученика.</b>'}
    return json.loads(authorise)


async def authorise_raw_request(client: aiohttp.ClientSession, captcha: str, captcha_id: str,
                                user_login: str, user_password: str) -> str:
    async with client.post(
        'https://lycreg.urfu.ru',
        data=f'{{"t":"pupil", "l":"{user_login}", "p":"{user_password}", "f":"login", '
             f'"ci":{captcha_id}, "c":{captcha} }}',
    ) as response:
        assert response.status == 200, 'Login-function response is not 200'
        return await response.text()


async def tabel_get_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        'https://lycreg.urfu.ru',
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"tabelGet","z":["{user_login}"]}}',
    ) as response:
        assert response.status == 200, 'tabelGet-function response is not 200'
        return await response.text()


async def subj_list_raw_request(client: aiohttp.ClientSession, user_login: str, user_token: str) -> str:
    async with client.post(
        'https://lycreg.urfu.ru',
        data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"subjList"}}',
    ) as response:
        assert response.status == 200, 'subjList-function response is not 200'
        return await response.text()


async def get_subj_list(client: aiohttp.ClientSession, user_login: str, user_token: str):
    return sesc_json.SESC_JSON['default_subjects'] | sesc_json.SESC_JSON.setdefault(
        'subject_list',
        json.loads(await subj_list_raw_request(client=client, user_login=user_login, user_token=user_token)),
    )


async def fetch_captcha(client: aiohttp.ClientSession) -> tuple[tempfile.TemporaryFile, int]:
    async with client.get('https://lycreg.urfu.ru/cpt.a') as response:
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
