import asyncio
import pathlib
import smtplib
import sys
from email.message import EmailMessage

import aiohttp

import scrap


async def main():
    categorized_urls = {
        "https://g1.globo.com/educacao/": "Educação",
        "https://g1.globo.com/ciencia-e-saude/": "Saúde",
        "https://g1.globo.com/monitor-da-violencia/": "Segurança",
        "https://g1.globo.com/natureza/": "Meio ambiente e sustentabilidade",
        "https://g1.globo.com/economia/": "Economia",
    }

    nc = scrap.NewsCollection()

    async with aiohttp.ClientSession() as session:
        for url, raw_data in await scrap.scrap_news(session=session, urls=categorized_urls.keys()):
            for parsed_data in scrap.parse_news(category=categorized_urls[url], raw_data=raw_data, max_days_elapsed=1):
                nc.add(parsed_data)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            email = sys.argv[1]
            password = sys.argv[2]

            message = EmailMessage()
            message["From"] = email
            message["To"] = email
            message["Subject"] = "Recent News"
            message.set_content(
                nc.to_styled_email_str(0, 0, 4, pathlib.Path("templates/news.html")),
                subtype="html",
            )

            smtp.login(email, password)
            smtp.send_message(message)


if __name__ == "__main__":
    asyncio.run(main())
