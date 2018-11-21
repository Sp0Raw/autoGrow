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
gpio.setcfg(port.PA20, gpio.OUTPUT)  ## Init  port 
#gpio.output(port.PA20, gpio.LOW)     # Turn RELAY => ON 

gpio.setcfg(port.PA10, gpio.OUTPUT)  ## Init  port

#sleep(2)
gpio.output(port.PA20, gpio.HIGH)    # Turn RELAY => OFF


# Relay module K2
#gpio.setcfg(port.PA10, gpio.OUTPUT)
gpio.output(port.PA10, gpio.LOW)    # Turn RELAY => ON
#sleep(2)
#gpio.output(port.PA10, gpio.HIGH)   # Turn RALAY => OFF

