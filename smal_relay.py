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


# Relay module LK1
gpio.setcfg(port.PG8, gpio.OUTPUT)
gpio.output(port.PG8, gpio.HIGH)
sleep(2)
#gpio.output(port.PG8, gpio.LOW)

# Relay module LK2
gpio.setcfg(port.PG9, gpio.OUTPUT)
gpio.output(port.PG9, gpio.HIGH)
sleep(2)
#gpio.output(port.PG9, gpio.LOW)

# Relay module LK3
gpio.setcfg(port.PG6, gpio.OUTPUT)
gpio.output(port.PG6, gpio.HIGH)
sleep(2)
#gpio.output(port.PG6, gpio.LOW)





