import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
########################
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)


while 1==1:
  #GPIO.output(26, False)
  time.sleep(1)
  GPIO.output(26, True)
  time.sleep(1)

  GPIO.output(19, False)
  time.sleep(1)
  GPIO.output(19, True)
  time.sleep(1)

  #GPIO.output(13, False)
  time.sleep(1)
  GPIO.output(13, True)
  time.sleep(1)

  #GPIO.output(6, False)
  time.sleep(1)
  GPIO.output(6, True)
  time.sleep(1)

  #GPIO.output(5, False)
  time.sleep(1)
  GPIO.output(5, True)
  time.sleep(1)
  
  #GPIO.output(22, False)
  time.sleep(1)
  GPIO.output(22, True)
  time.sleep(1)

  #GPIO.output(27, False)
  time.sleep(1)
  GPIO.output(27, True)
  time.sleep(1)

  #GPIO.output(17, False)
  time.sleep(1)
  GPIO.output(17, True)
  time.sleep(1)

###########################################


  #GPIO.output(18, False)
  time.sleep(1)
  GPIO.output(18, True)
  time.sleep(1)

  GPIO.output(23, False)
  time.sleep(1)
  #GPIO.output(23, True)
  time.sleep(1)

  GPIO.output(24, False)
  time.sleep(1)
  #GPIO.output(24, True)
  time.sleep(1)    
