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
from bs4 import BeautifulSoup


@dataclasses.dataclass
class NewsInfo:
    title: str
    summary: str
    url: str
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
                news=self,
                titleBlankLines=titleBlankLines,
                summaryBlankLines=summaryBlankLines,
                urlBlankLines=urlBlankLines,
            )
        )


# I don't know what to name this class, so this will stay like this for a while
# Should these dataclasses be frozen?
@dataclasses.dataclass
class NewsCollection:
    news: defaultdict[str, list[NewsInfo]] = dataclasses.field(default_factory=lambda: defaultdict(list))

    def ToEmailStr(self, titleBlankLines: int, summaryBlankLines: int, urlBlankLines: int) -> str:
        return "".join(
            map(lambda newsItem: newsItem.ToEmailStr(titleBlankLines, summaryBlankLines, urlBlankLines), self.news)
        )

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

        # I have a bad felling about this code
        # and I also have a bad felling about the templates
        return "".join(
            map(
                lambda newsCollection: template.render(
                    category=newsCollection[0],
                    newsCollection=newsCollection[1],
                    titleBlankLines=titleBlankLines,
                    summaryBlankLines=summaryBlankLines,
                    urlBlankLines=urlBlankLines,
                ),
                self.news.items(),
            )
        )

    def AddNew(self, news: NewsInfo):
        self.news[news.category].append(news)


class AbstractNewsScrapper(abc.ABC):
    @abc.abstractmethod
    def FilterInfo(self, info: str) -> str:
        pass

    @abc.abstractmethod
    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[str]) -> tuple[dict]:
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

    async def ScrapNews(self, session: aiohttp.ClientSession, urls: Iterable[str]) -> tuple[dict]:
        async def G1News(url: str) -> dict:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "lxml")
                script = soup.select("#bstn-fd-launcher > script:nth-child(3)")[0]

                return json.loads(self.FilterInfo(str(script)))

        tasks = (asyncio.create_task(G1News(url)) for url in urls)

        return await asyncio.gather(*tasks)


class G1Parser(AbstractNewsParser):
    def ParseNews(self, category: str, rawData: dict) -> Generator[NewsInfo, None, None]:
        for item in rawData["items"]:
            # Some of the dates in the file have a "Z" at the end
            # of the string representation of the date and some don't,
            # so I decided that it would be better to do this way.
            date = item["created"].split("T")[0].split("-")
            newsTime = datetime.date(int(date[0]), int(date[1]), int(date[2]))
            today = datetime.date.today()
            timeElapsed = today - newsTime

            # for now, I'll let this be a hardcoded date, but in the near future
            # I'll change this to a function parameter.
            if timeElapsed.days > 1:
                continue

            yield NewsInfo(
                title=item["content"]["title"],
                summary=item["content"]["summary"],
                url=item["content"]["url"],
                category=category,
            )
