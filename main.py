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
import dotenv
import aiohttp

# This is ok for now
def TimeUntil12pm():
    return 60 * 60 * 12

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
            rawData = await scrap.GetLatestG1News(session, urls)
            parsedDataSet = (scrap.ParseNews(newsRawData)
                            for newsRawData in rawData)

            for parsedData in parsedDataSet:
                for newsInfo in parsedData:
                    message += mail.ParseNewsToEmailMessageStr(newsInfo, 2, 2, 3)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                emailInfo = dotenv.dotenv_values(".env")
                emailMessage = mail.CreateMessage(
                    emailInfo["EMAIL"], emailInfo["EMAIL"], "Recent news", message
                )
                print(emailMessage)

                smtp.login(emailInfo["EMAIL"], emailInfo["PASSWORD"])

                smtp.send_message(emailMessage)

            print("message sent")
            time.sleep(TimeUntil12pm())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
