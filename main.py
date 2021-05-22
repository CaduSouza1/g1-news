# import smtplib
# import dotenv
# import imghdr
# from email.message import EmailMessage
import bs4
from bs4.element import Script
import requests
import json
from bs4 import BeautifulSoup
# emailInfo = dotenv.dotenv_values(".env")

# msg = EmailMessage()
# msg["From"] = emailInfo["EMAIL"]
# msg["To"] = emailInfo["EMAIL"]
# msg["Subject"] = "Grab m'dick"
# msg.set_content("Ha")

# with open("ddd.jpg", "rb") as f:
#     msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=f.name)

# # with smtplib.SMTP("localhost", 1025) as smtp:
# with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#     smtp.login(emailInfo["EMAIL"], emailInfo["PASSWORD"])

#     smtp.send_message(msg)

response = requests.get("https://g1.globo.com/educacao/")
response.raise_for_status()
