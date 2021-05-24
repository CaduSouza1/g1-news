import mail
import scrap

a = mail.CreateMessage("a", "b", "c", mail.ParseNewsToEmailMessageStr(
    scrap.NewsInfo("a", "v", "c"),
    2, 2, 1
))

print(a)