import argparse
import sys


#import the library
from pyA20.gpio import gpio
from pyA20.gpio import port
from time import sleep

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('name', nargs='?')

    return parser

gpio.init()
parser = createParser()
numComPort = parser.parse_args(sys.argv[1:])
turnVal = format(numComPort.name)

gpio.setcfg(port.PG9, gpio.OUTPUT)  ## Init  PIN an set is ON
if turnVal == "on" or turnVal=="1" or turnVal =="on+" or  turnVal =="11":
    gpio.output(port.PG9, gpio.HIGH)     # Turn RELAY => OFF
elif ((turnVal == "off" or turnVal == "0") or (turnVal == "off+" or turnVal == "00")):
    gpio.output(port.PG9, gpio.LOW)     # Turn RELAY => ON
