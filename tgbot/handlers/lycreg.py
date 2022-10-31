import aiogram.types
import aiohttp
import config
import dispatcher
import PIL
import pyscreeze
import tempfile


try:
    import simplejson as json
except ImportError:
    import json


@dispatcher.dp.message_handler(commands=['lycreg'])
async def lycreg(message: aiogram.types.Message) -> None:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
        cpt_file, cpt_id = await fetch_captcha(client)
        assert cpt_id is not None, 'X-Cpt header doesn\'t exists'
        login = await lycreg_authorize(
            client=client,
            cpt=await solve_captcha(cpt_file),
            cpt_id=cpt_id,
            login='',
            pwd='',
        )
        cpt_file.close()
        await message.reply(f'<code>{login}</code>', reply=False)


async def lycreg_authorize(client: aiohttp.ClientSession, cpt: str, cpt_id: str, login: str, pwd: str) -> dict:
    async with client.post(
        'https://lycreg.urfu.ru',
        data=f'{{"t":"pupil", "l":"{login}", "p":"{pwd}", "f":"login", "ci":{cpt_id}, "c":{cpt} }}',
    ) as resp:
        assert resp.status == 200, 'login-function response is not 200'
        response = await resp.text()
        assert '¤' in response, 'Bad login response'
        return json.loads(response)


async def fetch_captcha(client: aiohttp.ClientSession) -> tuple[tempfile.TemporaryFile, int]:
    async with client.get('https://lycreg.urfu.ru/cpt.a') as resp:
        assert resp.status == 200, '/cpt.a response status is not 200'
        fp = tempfile.TemporaryFile(suffix='.png')
        fp.write(await resp.read())
        fp.seek(0)
        return fp, resp.headers.get('X-Cpt')


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
