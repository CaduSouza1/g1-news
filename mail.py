import scrap
from email.message import EmailMessage
import jinja2


def ParseNewsToEmailStr(
    info: scrap.NewsInfo,
    titleBlankLines: int = 1,
    summaryBlankLines: int = 1,
    urlBlankLines: int = 1,
    styleFolderPath: str = None,
    styleFilename: str = None
) -> str:
    if styleFolderPath:
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(styleFolderPath),
            autoescape=jinja2.select_autoescape()
        )

        return env.get_template(styleFilename).render(
            title=info.title,
            titleBlankLines=titleBlankLines,
            summary=info.summary,
            summaryBlankLines=summaryBlankLines,
            url=info.url,
            urlBlankLines=urlBlankLines
        )

    return info.title + "\n" * titleBlankLines + info.summary + "\n" * summaryBlankLines + info.url + "\n" * urlBlankLines


def CreateMessage(From: str, to: str, subject: str, content: str, styled: bool = False) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = From
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(content, subtype="html")

    return msg
