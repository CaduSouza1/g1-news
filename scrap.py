import dataclasses
from bs4 import BeautifulSoup
import aiohttp
import datetime
import asyncio
import json


@dataclasses.dataclass
class NewsInfo:
    title: str
    summary: str
    url: str
    dateCreated: datetime.time


async def GetLatestG1News(session: aiohttp.ClientSession, urls: list[str]) -> list[dict]:
    async def G1News(url: str) -> dict:
        async with session.get(url) as response:
            info = await response.text()
            soup = BeautifulSoup(info, "html.parser")

            news = soup.find("main")

            newsGrid = news.find_all("div", recursive=False)[2]

            info = newsGrid.find_all("div", recursive=False)[-1]
            script= str(info.div.div.div.script)
            jsonInfoStart = script.find('"config":') - 1
            jsonInfoEnd = script.find(", {lazy")

            newsRawData = script[jsonInfoStart:jsonInfoEnd]

            return json.loads(newsRawData)

    tasks = [
        asyncio.create_task(G1News(url)) for url in urls
    ]

    results = await asyncio.gather(*tasks)
    
    return results

def ParseNews(newsRawData: dict) -> list[NewsInfo]:
    pass
