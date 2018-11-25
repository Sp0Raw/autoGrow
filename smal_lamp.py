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


# Relay module LK3
gpio.setcfg(port.PD14, gpio.OUTPUT)
gpio.output(port.PD14, gpio.HIGH)
sleep(2)
#gpio.output(port.PD14, gpio.LOW)





