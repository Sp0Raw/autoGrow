import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    input_state = GPIO.input(25)
    if input_state == False:
        print('Button Pressed')
        time.sleep(0.2)
        GPIO.output(26, False)
    else:
        GPIO.output(26, True)
