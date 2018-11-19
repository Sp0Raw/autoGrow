import argparse

#import the library
from pyA20.gpio import gpio
from pyA20.gpio import port
from time import sleep


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('name', nargs='?')

    return parser


#initialize the gpio module
gpio.init()


# Relay module K1
gpio.setcfg(port.PA20, gpio.OUTPUT)
gpio.output(port.PA20, gpio.LOW)
sleep(2)
gpio.output(port.PA20, gpio.HIGH)


# Relay module K2
gpio.setcfg(port.PA10, gpio.OUTPUT)
gpio.output(port.PA10, gpio.LOW)
sleep(2)
gpio.output(port.PA10, gpio.HIGH)


# Relay module K3
gpio.setcfg(port.PA9, gpio.OUTPUT)
gpio.output(port.PA9, gpio.LOW)
sleep(2)
gpio.output(port.PA9, gpio.HIGH)


# Relay module K4
gpio.setcfg(port.PA8, gpio.OUTPUT)
gpio.output(port.PA8, gpio.LOW)
sleep(2)
gpio.output(port.PA8, gpio.HIGH)


# Relay module K5
gpio.setcfg(port.PA7, gpio.OUTPUT)
gpio.output(port.PA7, gpio.LOW)
sleep(2)
gpio.output(port.PA7, gpio.HIGH)


# Relay module K6
gpio.setcfg(port.PC7, gpio.OUTPUT)
gpio.output(port.PC7, gpio.LOW)
sleep(2)
gpio.output(port.PC7, gpio.HIGH)


# Relay module K7
gpio.setcfg(port.PC4, gpio.OUTPUT)
gpio.output(port.PC4, gpio.LOW)
sleep(2)
gpio.output(port.PC4, gpio.HIGH)


# Relay module K8
gpio.setcfg(port.PD14, gpio.OUTPUT)
gpio.output(port.PD14, gpio.LOW)
sleep(2)
gpio.output(port.PD14, gpio.HIGH)


# Relay module LK1
gpio.setcfg(port.PG8, gpio.OUTPUT)
gpio.output(port.PG8, gpio.HIGH)
sleep(2)
gpio.output(port.PG8, gpio.LOW)

# Relay module LK2
gpio.setcfg(port.PG9, gpio.OUTPUT)
gpio.output(port.PG9, gpio.HIGH)
sleep(2)
gpio.output(port.PG9, gpio.LOW)

# Relay module LK3
gpio.setcfg(port.PG6, gpio.OUTPUT)
gpio.output(port.PG6, gpio.HIGH)
sleep(2)
gpio.output(port.PG6, gpio.LOW)




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
