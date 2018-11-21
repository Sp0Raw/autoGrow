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


# Relay module K2
gpio.setcfg(port.PG9, gpio.OUTPUT)  ## Init  port 
gpio.output(port.PG9, gpio.HIGH)     # Turn RELAY => ON 
sleep(2)
#gpio.output(port.PG9, gpio.LOW)    # Turn RELAY => OFF
#sleep(2)
