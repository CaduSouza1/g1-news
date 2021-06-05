from datetime import datetime, timedelta
import asyncio
import scrap
import mail
import smtplib
import time
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

    while True:
        message = ""
        async with aiohttp.ClientSession() as session:

            for rawData in await scrap.GetLatestG1News(session, urls):
                for parsedData in scrap.ParseNews(rawData):
                    message += mail.ParseNewsToEmailStr(
                        parsedData, 0, 0, 2, "templates", "news.html"
                    )

            with (
                smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp,
                open("receivers.json", "r") as jsonFile
            ):
                sender = dotenv.dotenv_values(".env")
                receivers = json.load(jsonFile)

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

            nextMessageTime = (datetime.now().replace(
                hour=12, minute=0, second=0) + timedelta(1)) - datetime.now()
            time.sleep(nextMessageTime.total_seconds())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
