# import smtplib
# import dotenv
# import imghdr
# from email.message import EmailMessage
# emailInfo = dotenv.dotenv_values(".env")

#     smtp.send_message(msg)

import asyncio
import scrap
import mail
import smtplib
import time
import pytz
import datetime
import dotenv
import aiohttp

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
            print("Preparing message")

            for rawData in await scrap.GetLatestG1News(session, urls):
                for parsedData in scrap.ParseNews(rawData):
                    message += mail.ParseNewsToEmailMessageStr(parsedData, 2, 2, 3)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                emailInfo = dotenv.dotenv_values(".env")
                emailMessage = mail.CreateMessage(
                    emailInfo["EMAIL"], emailInfo["EMAIL"], "Recent news", message
                )
                # print(emailMessage)

                smtp.login(emailInfo["EMAIL"], emailInfo["PASSWORD"])

                smtp.send_message(emailMessage)

            print("message sent")
            nextMessageTime = (datetime.datetime.now().replace(hour=12, minute=0, second=0) + datetime.timedelta(1)) - datetime.datetime.now()
            print(f"Waiting {nextMessageTime.total_seconds()}s")
            time.sleep(nextMessageTime.total_seconds())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
