from __future__ import annotations

import re

import aiohttp

from tgbot.redis_client import get_cache, set_cache

_SCHEDULE_URL = 'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii'
_CACHE_KEY = 'schedule:selects'
_TTL = 3600


def _parse_selects(html: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for m in re.finditer(r'<select[^>]*data-name="([^"]+)"[^>]*>(.*?)</select>', html, re.DOTALL):
        name = m.group(1)
        if name not in ('group', 'auditory', 'teacher'):
            continue
        options: dict[str, str] = {}
        for opt in re.finditer(r'<option[^>]*value="(\d+)"[^>]*>([^<]+)</option>', m.group(2)):
            val, text = opt.group(1), opt.group(2).strip()
            if val != '0':
                options[text] = val
        result[name] = options
    return result


async def get_schedule_data() -> dict[str, dict[str, str]]:
    cached = await get_cache(_CACHE_KEY)
    if cached:
        return cached

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(_SCHEDULE_URL) as resp:
            html = await resp.text()

    data = _parse_selects(html)
    await set_cache(_CACHE_KEY, data, ttl=_TTL)
    return data
