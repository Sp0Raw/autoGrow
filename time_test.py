import datetime
import time

# Значение: datetime.datetime(2017, 4, 5, 0, 18, 51, 980187)
now = datetime.datetime.now()
time.sleep(5)
then = datetime.datetime.now() ###datetime.datetime(2017, 2, 26)

# Кол-во времени между датами.
delta =  then - now

print(delta.days)  # 38
print(delta.seconds)  # 1131w

