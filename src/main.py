import asyncio
import pathlib

import scrap
import smtplib
import dotenv
import aiohttp
import json

from email.message import EmailMessage


async def main():
    categorizedUrls = {
        "https://g1.globo.com/educacao/": "Educação",
        "https://g1.globo.com/ciencia-e-saude/": "Saúde",
        "https://g1.globo.com/monitor-da-violencia/": "Segurança",
        "https://g1.globo.com/natureza/": "Meio ambiente e sustentabilidade",
        "https://g1.globo.com/economia/": "Economia"
    }

    nc = scrap.NewsCollection()

    async with aiohttp.ClientSession() as session:
        scrapper = scrap.G1Scrapper()
        parser = scrap.G1Parser()

        for url, rawData in await scrapper.ScrapNews(session, categorizedUrls.keys()):
            for parsedData in parser.ParseNews(categorizedUrls[url], rawData):
                nc.AddNew(parsedData)

        with (
            smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp,
            open("receivers.json", "r") as jsonFile
        ):
            receivers = json.load(jsonFile)
            sender = dotenv.dotenv_values(".env")
            
            message = EmailMessage()
            message["From"] = sender["EMAIL"]
            message["To"] = receivers["emails"]
            message["Subject"] = "Recent News"
            message.set_content(nc.ToStyledEmailStr(0, 0, 4, pathlib.Path("templates/news.html")), subtype="html")

            smtp.login(
                sender["EMAIL"],
                sender["PASSWORD"]
            )

            smtp.send_message(message)


asyncio.get_event_loop().run_until_complete(main())
