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



#try:
gpio.init()
parser = createParser()
numComPort = parser.parse_args(sys.argv[1:])
turnVal = format(numComPort.name)

gpio.setcfg(port.PA20, gpio.OUTPUT)  ## Init  PIN an set is ON
if turnVal == "on" or turnVal=="1" or turnVal =="on+" or  turnVal =="11":
    gpio.output(port.PA20, gpio.HIGH)     # Turn RELAY => OFF
else:
    gpio.output(port.PA20, gpio.LOW)     # Turn RELAY => ON
sleep(1)

gpio.setcfg(port.PA10, gpio.OUTPUT)  ## Init  PIN
gpio.output(port.PA10, gpio.HIGH)    # Turn RELAY => OFF
sleep(3)

if turnVal == "on" or turnVal=="1":
    print ("HP0 TURN ON" )

    gpio.output(port.PA20, gpio.HIGH)    # Turn RELAY => OFF
    sleep(2)
    gpio.output(port.PA10, gpio.LOW)     # Turn RELAY => ON

    sleep(3)
    gpio.output(port.PA10, gpio.HIGH)    # Turn RELAY => ON

elif (turnVal == "off" or turnVal == "0"):
    print ("!!!HP0 turn OFF!!!")
    gpio.output(port.PA20, gpio.HIGH)    # Turn RELAY => OFF


if turnVal == "on+" or turnVal=="11":
    print ("HP0 TURN No Limited ON " )

    gpio.output(port.PA20, gpio.HIGH)    # Turn RELAY => OFF
    sleep(2)
    gpio.output(port.PA10, gpio.LOW)     # Turn RELAY => ON

elif (turnVal == "off+" or turnVal == "00"):
    print ("!!!HP0 turn No Limited OFF!!!")


#except Exception:
#    print ("Error!")
