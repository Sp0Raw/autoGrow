import argparse

#import the library
from pyA20.gpio import gpio
from pyA20.gpio import port
from time import sleep


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('name', nargs='?')

    return parser


# Read pin 40 
gpio.setcfg(port.PG7, gpio.INPUT)   #Configure PE11 as input
gpio.setcfg(port.PG7, 0)   #Same as above

gpio.pullup(port.PG7, 0)   #Clear pullups
gpio.pullup(port.PG7, gpio.PULLDOWN)    #Enable pull-down
gpio.pullup(port.PG7, gpio.PULLUP)      #Enable pull-up

while True:
      if gpio.input(port.PG7) != 1:
         gpio.output(port.PA20, gpio.LOW)
         gpio.output(port.PA20, 0)
	 print ("PUSH!!!")
      else:
         gpio.output(port.PA20, gpio.HIGH)
         gpio.output(port.PA20, 1)
