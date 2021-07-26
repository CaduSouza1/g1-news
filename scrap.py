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

    def ToEmailStr(self) -> str:
        pass


@dataclasses.dataclass
class NewsCollection:
    categories: dict[str, list[NewsInfo]]  # {"education": [news1, news2, ...]}

    def ToEmailStr(self) -> str:
        pass

    def Styled(self) -> str:
        pass


class AbstractNewsScrapper(abc.ABC):
    @abc.abstractmethod
    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[str]) -> tuple[dict]:
        pass


class AbstractNewsParser(abc.ABC):
    @abc.abstractmethod
    def ParseNews(self, rawData: dict) -> Generator[NewsInfo, None, None]:
        pass


class G1Scrapper(AbstractNewsScrapper):
    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[str]) -> tuple[dict]:
        async def G1News(url: str) -> dict:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

                # for some reason, this is the only way I got this code to work
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
            date = (
                item["created"].split("T")[0].split("-")
            )  # Some of the dates in the file have a "Z" at the end of the string representation of the date.
            newsTime = datetime.date(int(date[0]), int(date[1]), int(date[2]))
            today = datetime.date.today()
            timeElapsed = today - newsTime

            if timeElapsed.days > 1:
                continue

            yield NewsInfo(
                title=item["content"]["title"],
                summary=item["content"]["summary"],
                url=item["content"]["url"]
            )
