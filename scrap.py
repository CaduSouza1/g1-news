import dataclasses
from bs4 import BeautifulSoup
import aiohttp
import datetime
import pytz
import asyncio
import json


@dataclasses.dataclass
class NewsInfo:
    title: str
    summary: str
    url: str


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
    parsedData = []

    for item in newsRawData["items"]:
        date = item["created"].split("T")[0].split("-")
        newsTime = datetime.date(int(date[0]), int(date[1]), int(date[2]))

        today = datetime.date.today()

        timeElapsed = today - newsTime

        if timeElapsed.days > 1:
            continue

        parsedData.append(
            NewsInfo(
                title = item["content"]["title"],
                summary = item["content"]["summary"],
                url = item["content"]["url"]
            )
        )

    return parsedData