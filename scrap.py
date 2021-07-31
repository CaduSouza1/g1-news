import abc
import asyncio
from collections import defaultdict
import dataclasses
import datetime
import json
import pathlib
from typing import Generator, Iterable

import aiohttp
import jinja2
import yarl
from bs4 import BeautifulSoup

# import enum


# class Category(enum.IntEnum):
#     EDUCATION = enum.auto()
#     HEALTH = enum.auto()

#     def ToStr(self) -> str:
#         translationTable = {
#             self.EDUCATION: "Education",
#             self.HEALTH: "Health"
#         }

#         return translationTable[self.value]


@dataclasses.dataclass
class NewsInfo:
    title: str
    summary: str
    url: yarl.URL
    category: str

    def ToEmailStr(self, titleBlankLines: int, summaryBlankLines: int, urlBlankLines: int) -> str:
        return (
            self.title
            + "\n" * titleBlankLines
            + self.summary
            + "\n" * summaryBlankLines
            + self.url
            + "\n" * urlBlankLines
        )

    def ToStyledEmailStr(
        self, titleBlankLines: int, summaryBlankLines: int, urlBlankLines: int, styleFilepath: pathlib.Path
    ) -> str:
        return (
            jinja2.Environment(
                loader=jinja2.FileSystemLoader(styleFilepath.parent), autoescape=jinja2.select_autoescape()
            )
            .get_template(styleFilepath.name)
            .render(
                title=self.title,
                titleBlankLines=titleBlankLines,
                summary=self.summary,
                summaryBlankLines=summaryBlankLines,
                url=self.url,
                urlBlankLines=urlBlankLines,
            )
        )


@dataclasses.dataclass
class NewsCollection:
    news: list[NewsInfo]

    # def ToEmailStr(self, categorize: bool) -> str:
    #     if categorize:
    #         categorizedNews = self.Categorize()

    def ToStyledEmailStr(
        self, titleBlankLines: int, summaryBlankLines: int, urlBlankLines: int, styleFilepath: pathlib.Path
    ) -> str:
        """Creates an html string based on a template defined at `styleFilepath`

        Args:
            titleBlankLines (int): Blank lines added at the end of the title
            summaryBlankLines (int): Blank lines added at the end of the summary
            urlBlankLines (int): Blank lines at the end of the url
            styleFilepath (pathlib.Path): Path to the file containing the template

        Returns:
            str: Html string representation of the news objects in this collection
        """

        template = jinja2.Environment(
            loader=jinja2.FileSystemLoader(styleFilepath.parent), autoescape=jinja2.select_autoescape()
        ).get_template(styleFilepath.name)

        return "".join(
            map(
                lambda newsCollection: template.render(
                    category=newsCollection[0],
                    newsCollection=newsCollection[1],
                    titleBlankLines=titleBlankLines,
                    summaryBlankLines=summaryBlankLines,
                    urlBlankLines=urlBlankLines,
                ),
                self.Categorize().items(),
            )
        )

    def Categorize(self) -> dict[str, list[NewsInfo]]:
        categories = defaultdict(list)
        for newsItem in self.news:
            categories[newsItem.category].append(newsItem)

        return categories


class AbstractNewsScrapper(abc.ABC):
    @abc.abstractmethod
    def FilterInfo(self, info: str) -> str:
        pass

    @abc.abstractmethod
    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[yarl.URL]) -> tuple[dict]:
        pass


class AbstractNewsParser(abc.ABC):
    @abc.abstractmethod
    def ParseNews(self, rawData: dict) -> Generator[NewsInfo, None, None]:
        pass


class G1Scrapper(AbstractNewsScrapper):
    def FilterInfo(self, info: str) -> str:
        infoStart = info.find('"config":') - 1
        infoEnd = info.rfind(", {lazy")

        return info[infoStart:infoEnd]

    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[yarl.URL]) -> tuple[dict]:
        async def G1News(url: yarl.URL) -> dict:
            print(f"Requesting {url}")
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

                # for some reason, this is the only way I got this code to work
                news = soup.find("main")

                newsGrid = news.find_all("div", recursive=False)[2]

                info = newsGrid.find_all("div", recursive=False)[-1]
                script = str(info.div.div.div.script)

                print(f"Request finished")
                return json.loads(self.FilterInfo(script))

        tasks = (asyncio.create_task(G1News(url)) for url in urls)

        return await asyncio.gather(*tasks)


class G1Parser(AbstractNewsParser):
    def ParseNews(self, category: str, rawData: dict) -> Generator[NewsInfo, None, None]:
        for item in rawData["items"]:
            date = (
                item["created"].split("T")[0].split("-")
            )  # Some of the dates in the file have a "Z" at the end of the string representation of the date.
            newsTime = datetime.date(int(date[0]), int(date[1]), int(date[2]))
            today = datetime.date.today()
            timeElapsed = today - newsTime

            # if timeElapsed.days > 1:
            #     continue

            yield NewsInfo(
                title=item["content"]["title"],
                summary=item["content"]["summary"],
                url=item["content"]["url"],
                category=category,
            )
