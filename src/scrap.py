import asyncio
import datetime
import json
import pathlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Generator, Iterable

import aiohttp
import jinja2
from bs4 import BeautifulSoup


@dataclass
class NewsInfo:
    title: str
    summary: str
    url: str
    category: str


# I don't know what to name this class, so this will stay like this for a while
# Should these dataclasses be frozen?
@dataclass
class NewsCollection:
    news: defaultdict[str, list[NewsInfo]] = field(default_factory=lambda: defaultdict(list))

    def to_styled_email_str(
        self,
        title_blank_lines: int,
        summary_blank_lines: int,
        url_blank_lines: int,
        style_filepath: pathlib.Path,
    ) -> str:
        """Creates an html string based on a template defined at `style_filepath`

        Args:
            title_blank_lines (int): Blank lines added at the end of the title
            summary_blank_lines (int): Blank lines added at the end of the summary
            url_blank_lines (int): Blank lines at the end of the url
            style_filepath (pathlib.Path): Path to the file containing the template

        Returns:
            str: Html string representation of the news objects in this collection
        """

        template = jinja2.Environment(
            loader=jinja2.FileSystemLoader(style_filepath.parent),
            autoescape=jinja2.select_autoescape(),
        ).get_template(style_filepath.name)

        return "".join(
            map(
                lambda news_collection: template.render(
                    category=news_collection[0],
                    news_collection=news_collection[1],
                    title_blank_lines=title_blank_lines,
                    summary_blank_lines=summary_blank_lines,
                    url_blank_lines=url_blank_lines,
                ),
                self.news.items(),
            )
        )

    def add(self, news: NewsInfo):
        self.news[news.category].append(news)


def filter_info(info: str) -> str:
    info_start = info.find('"config":') - 1
    info_end = info.rfind(", {lazy")

    return info[info_start:info_end]


async def scrap_news(session: aiohttp.ClientSession, urls: Iterable[str]) -> tuple[tuple[str, dict]]:
    async def G1News(url: str) -> tuple[str, dict]:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), "lxml")
            script = soup.select("#bstn-fd-launcher > script:nth-child(3)")[0]
            b = filter_info(str(script))
            a = json.loads(b)
            with open("f.json", "w") as f:
                f.write(b)

            with open("g.json", "w") as g:
                g.write(str(a["config"]))
            return (url, a)

    tasks = (asyncio.create_task(G1News(url)) for url in urls)

    return await asyncio.gather(*tasks)


def parse_news(category: str, raw_data: dict, max_days_elapsed: int) -> Generator[NewsInfo, None, None]:
    with open("q.json", "w") as f:
        f.write(raw_data.__str__())
    for item in raw_data["items"]:
        # Some of the dates in the file have a "Z" at the end
        # of the string representation of the date and some don't,
        # so I decided that it would be better to do this way.
        date = item["created"].split("T")[0].split("-")
        news_time = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        time_elapsed = datetime.date.today() - news_time

        if time_elapsed.days > max_days_elapsed:
            continue

        # for some reason, there is ONE. ONE entry on the input data that does not have a summary key.
        try:
            yield NewsInfo(
                title=item["content"]["title"],
                summary=item["content"]["summary"],
                url=item["content"]["url"],
                category=category,
            )
        except KeyError:
            continue
