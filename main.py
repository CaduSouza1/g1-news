import asyncio
import scrap
import mail
import smtplib
import dotenv
import aiohttp
import json


async def main():
    urls = [
        "https://g1.globo.com/educacao/",
        "https://g1.globo.com/ciencia-e-saude/",
        "https://g1.globo.com/monitor-da-violencia/",
        "https://g1.globo.com/economia/",
        "https://g1.globo.com/natureza/"
    ]

    message = ""
    async with aiohttp.ClientSession() as session:
        parser = scrap.G1Parser()
        scrapper = scrap.G1Scrapper()

        for rawData in await scrapper.ScrapNews(session, urls):
            for parsedData in parser.ParseNews(rawData):
                message += mail.ParseNewsToEmailStr(
                    parsedData, 0, 0, 2, "templates", "news.html"
                )

        with (
            smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp,
            open("receivers.json", "r") as jsonFile
        ):
            receivers = json.load(jsonFile)
            sender = dotenv.dotenv_values(".env")
            emailMessage = mail.CreateMessage(
                sender["EMAIL"],
                ", ".join(receivers["emails"]),
                "Recent news", message
            )

            smtp.login(
                sender["EMAIL"],
                sender["PASSWORD"]
            )

            smtp.send_message(emailMessage)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
