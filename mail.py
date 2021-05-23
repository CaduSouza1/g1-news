import smtplib
import scrap
from email.message import EmailMessage


def ParseNewsToEmailMessage(newsInfos: list[scrap.NewsInfo]) -> EmailMessage:
    pass


def CreateMessage(From: str, to: str, subject: str, content: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = From
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(content)
    
    return msg

# with smtplib.SMTP("localhost", 1025) as smtp:
# with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#     smtp.login(emailInfo["EMAIL"], emailInfo["PASSWORD"])

#     smtp.send_message(msg)
