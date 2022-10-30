import aiogram
import aiogram.types
import aiohttp
import config
import dispatcher
import tempfile
import PIL
import pyscreeze
import time

@dispatcher.dp.message_handler(commands=['lycreg'])
async def lycreg(message: aiogram.types.Message) -> None:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
        fp = await fetch_captcha(client)
        image = fp.read()
        captcha, time = await solve_captcha(fp)
        fp.close()
        await message.reply_photo(photo=image, caption=f'{captcha}, {time=:.4f}', reply=False)

async def fetch_captcha(client: aiohttp.ClientSession) -> tempfile.TemporaryFile:
    async with client.get('https://lycreg.urfu.ru/cpt.a') as resp:
        assert resp.status == 200
        fp = tempfile.TemporaryFile(suffix='.png')
        fp.write(await resp.read())
        fp.seek(0)
        return fp

async def solve_captcha(file: tempfile.TemporaryFile) -> str:
    _fsasd = time.time()
    captcha = PIL.Image.open(file).convert('RGBA')
    results = []
    numbers_files = {config.BASE_DIR / 'numbers' / f'{i}_{j}.png': str(i) for i in range(10) for j in range(1, 3)}
    for (file_name, number) in numbers_files.items():
        number_image = PIL.Image.open(file_name)
        while True:
            try:
                result = pyscreeze.locate(number_image, captcha, grayscale=True)
                if result is None:
                    break
                result = (result[0], result[1], result[0] + result[2], result[1] + result[3])
                PIL.ImageDraw.Draw(captcha).rectangle(result, fill=0)
                results.append((number, result[0]))
            except StopIteration:
                break
    results = [x[0] for x in sorted(results, key=lambda x: x[1])]
    code = ''.join(results)
    return code, time.time() - _fsasd
