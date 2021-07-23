import abc
import asyncio
import dataclasses
import datetime
import json
from typing import Generator, Iterable

import aiohttp
from bs4 import BeautifulSoup


@dataclasses.dataclass
class NewsInfo:
    title: str
    summary: str
    url: str


class AbstractNewsScrapper(abc.ABC):

    @abc.abstractmethod
    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[str]) -> tuple[dict]:
        pass


class AbstractNewsParser(abc.ABC):

    @abc.abstractmethod
    def ParseNews(self, rawdata: dict) -> Generator[NewsInfo, None, None]:
        pass


class G1Scrapper(AbstractNewsScrapper):
    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[str]) -> tuple[dict]:
        async def G1News(url: str) -> dict:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

                news = soup.find("main")

                newsGrid = news.find_all("div", recursive=False)[2]

                info = newsGrid.find_all("div", recursive=False)[-1]
                script = str(info.div.div.div.script)
                jsonInfoStart = script.find('"config":') - 1
                jsonInfoEnd = script.rfind(", {lazy")

                newsRawData = script[jsonInfoStart:jsonInfoEnd]

                return json.loads(newsRawData)

        tasks = (asyncio.create_task(G1News(url)) for url in urls)

        return await asyncio.gather(*tasks)


class G1Parser(AbstractNewsParser):
    def ParseNews(self, rawData: dict) -> Generator[NewsInfo, None, None]:
        for item in rawData["items"]:
            date = item["created"].split("T")[0].split("-")
            newsTime = datetime.date(int(date[0]), int(date[1]), int(date[2]))
            today = datetime.date.today()
            timeElapsed = today - newsTime

            if timeElapsed.days > 1:
                continue

            yield NewsInfo(
                title=item["content"]["title"],
                summary=item["content"]["summary"],
                url=item["content"]["url"],
            )
