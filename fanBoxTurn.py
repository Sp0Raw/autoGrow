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


# Relay module K4
gpio.setcfg(port.PD14, gpio.OUTPUT)  ## Init  port 
gpio.output(port.PD14, gpio.LOW)     # Turn RELAY => ON 
#sleep(60)
#gpio.output(port.PD14, gpio.HIGH)    # Turn RELAY => OFF

