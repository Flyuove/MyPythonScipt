import time
import os
import datetime


while True:
    os.system("python3 -m scrapy crawl wifi")
    now = datetime.datetime.now()
    if (now.hour > 7 and now.hour < 10) or (now.hour > 17 and now.hour < 19):
        time.sleep(5)
    else:
        time.sleep(30)

# os.system("scrapy crawl wifi")


