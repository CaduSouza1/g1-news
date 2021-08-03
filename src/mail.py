from email.message import EmailMessage

def CreateMessage(From: str, to: str, subject: str, content: str, styled: bool = False) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = From
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(content, subtype="html")

    return msg
