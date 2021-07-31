import asyncio
import pathlib
import scrap
import mail
import smtplib
import dotenv
import aiohttp
import json

# import yarl

async def main():
    categorizedUrls = {
        "Educação": ["https://g1.globo.com/educacao/"],
        "Saúde": ["https://g1.globo.com/ciencia-e-saude/"],
        "Segurança": ["https://g1.globo.com/monitor-da-violencia/"],
        "Meio ambiente e sustentabilidade": ["https://g1.globo.com/natureza/"],
        "Economia": ["https://g1.globo.com/economia/"]
    }

    nc = scrap.NewsCollection([])

    async with aiohttp.ClientSession() as session:
        parser = scrap.G1Parser()
        scrapper = scrap.G1Scrapper()

        # This approach renders all the asynchronous methods useless, since there's only one url beeing passed to the function. 
        # I'll try to fix this as soon as possible, but for now I really don't know how without breaking the categorization.
        for category, urls in categorizedUrls.items():
            for rawData in await scrapper.ScrapNews(session, urls):
                for parsedData in parser.ParseNews(category, rawData):
                    nc.news.append(parsedData)

        with (
            smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp,
            open("receivers.json", "r") as jsonFile
        ):
            receivers = json.load(jsonFile)
            sender = dotenv.dotenv_values(".env")
            emailMessage = mail.CreateMessage(
                sender["EMAIL"],
                ", ".join(receivers["emails"]),
                "Recent news", nc.ToStyledEmailStr(0, 0, 2, pathlib.Path("templates/news_collection.html"))
            )

            smtp.login(
                sender["EMAIL"],
                sender["PASSWORD"]
            )

            smtp.send_message(emailMessage)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
