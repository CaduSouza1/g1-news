import datetime
import mail
import scrap

nextMessageTime = (datetime.datetime.now().replace(hour=12, minute=0, second=0) + datetime.timedelta(1)) - datetime.datetime.now().replace(hour=10)

print(datetime.datetime.now().replace(hour=12, minute=0, second=0))
print(nextMessageTime.total_seconds())