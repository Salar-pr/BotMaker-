import schedule
import datetime
import time



def print_date():
    print(datetime.datetime.now())
   


schedule.every(1).seconds.do(print_date)

while True:
    schedule.run_pending()
    time.sleep(1)
