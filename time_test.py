import datetime

# Значение: datetime.datetime(2017, 4, 5, 0, 18, 51, 980187)
now = datetime.datetime.now()

then = datetime.datetime(2017, 2, 26)

# Кол-во времени между датами.
delta = now - then

print(delta.days)  # 38
print(delta.seconds)  # 1131w
