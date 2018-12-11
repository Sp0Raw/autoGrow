#! /usr/bin/env python
import posix
import datetime
import time
import serial
import sys
import psycopg2
import argparse
from fcntl import ioctl

## for CPU temp
import io

## LCD
# requires RPi_I2C_driver.py
import RPi_I2C_driver

# For key press detect
import keyboard #Using module keyboard

# json parser
import json

from termcolor import colored

#import the library
from pyA20.gpio import gpio
from pyA20.gpio import port


print colored('hello', 'green'), colored('world', 'red')

#############################################
##   GIT
#############################################

#initialize the gpio module
gpio.init()

# Read pin 40
gpio.setcfg(port.PG7, gpio.INPUT)   #Configure PE11 as input
gpio.setcfg(port.PG7, 0)   #Same as above

gpio.pullup(port.PG7, 0)   #Clear pullups
gpio.pullup(port.PG7, gpio.PULLDOWN)    #Enable pull-down
gpio.pullup(port.PG7, gpio.PULLUP)      #Enable pull-up


mylcd = RPi_I2C_driver.lcd()
# test 2
mylcd.lcd_display_string("=== My GROW ===", 1)
mylcd.lcd_display_string(" Custom chars", 2)

# DB Connect
conn = psycopg2.connect('host=192.168.88.10 user=postgres password=pgsql dbname=postgres')

## Init home sensor val
home_hum = 0.0
home_temp = 0.0

## Init box sensor val
box_hum = 0.0
box_temp = 0.0

###  Init  Smal Relay module pins
# Relay module LK1
gpio.setcfg(port.PG8, gpio.OUTPUT)
gpio.output(port.PG8, gpio.HIGH)
#sleep(2)
#gpio.output(port.PG8, gpio.LOW)

# Relay module LK2
gpio.setcfg(port.PG9, gpio.OUTPUT)
gpio.output(port.PG9, gpio.HIGH)
#sleep(2)
#gpio.output(port.PG9, gpio.LOW)

# Relay module LK3
gpio.setcfg(port.PG6, gpio.OUTPUT)
gpio.output(port.PG6, gpio.HIGH)
#sleep(2)
#gpio.output(port.PG6, gpio.LOW)


###  Init  BIG Relay module pins
# Relay module LP1
gpio.setcfg(port.PA7, gpio.OUTPUT)
gpio.output(port.PA7, gpio.HIGH)


###
last_time_update = datetime.datetime.now()

# LCD info switch
lcdInf = -1

# HaveData
haveData = -1

# run loop with Out Delay
withOutDelay = 1

###

def get_cpu_temperature():
    """get cpu temperature using vcgencmd"""
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('name', nargs='?')

    return parser

class AM2320:
  I2C_ADDR = 0x5c
  I2C_SLAVE = 0x0703

  def __init__(self, i2cbus = 1):
    self._i2cbus = i2cbus

  @staticmethod
  def _calc_crc16(data):
    crc = 0xFFFF
    for x in data:
      crc = crc ^ x
      for bit in range(0, 8):
        if (crc & 0x0001) == 0x0001:
          crc >>= 1
          crc ^= 0xA001
        else:
          crc >>= 1
    return crc

  @staticmethod
  def _combine_bytes(msb, lsb):
    return msb << 8 | lsb


  def readSensor(self):
    fd = posix.open("/dev/i2c-%d" % self._i2cbus, posix.O_RDWR)

    ioctl(fd, self.I2C_SLAVE, self.I2C_ADDR)

    # wake AM2320 up, goes to sleep to not warm up and affect the humidity sens$
    # This write will fail as AM2320 won't ACK this write
    try:
      posix.write(fd, b'\0x00')
    except:
      pass
    time.sleep(0.001)  #Wait at least 0.8ms, at most 3ms

    # write at addr 0x03, start reg = 0x00, num regs = 0x04 */
    posix.write(fd, b'\x03\x00\x04')
    time.sleep(0.0016) #Wait at least 1.5ms for result

    # Read out 8 bytes of result data
    # Byte 0: Should be Modbus function code 0x03
    # Byte 1: Should be number of registers to read (0x04)
    # Byte 2: Humidity msb
    # Byte 3: Humidity lsb
    # Byte 4: Temperature msb
    # Byte 5: Temperature lsb
    # Byte 6: CRC lsb byte
    # Byte 7: CRC msb byte
    data = bytearray(posix.read(fd, 8))

    # Check data[0] and data[1]
    if data[0] != 0x03 or data[1] != 0x04:
      raise Exception("First two read bytes are a mismatch")

    # CRC check
    if self._calc_crc16(data[0:6]) != self._combine_bytes(data[7], data[6]):
      raise Exception("CRC failed")

    # Temperature resolution is 16Bit,
    # temperature highest bit (Bit15) is equal to 1 indicates a
    # negative temperature, the temperature highest bit (Bit15)
    # is equal to 0 indicates a positive temperature;
    # temperature in addition to the most significant bit (Bit14 ~ Bit0)
    # indicates the temperature sensor string value.
    # Temperature sensor value is a string of 10 times the
    # actual temperature value.
    temp = self._combine_bytes(data[4], data[5])
    if temp & 0x8000:
      temp = -(temp & 0x7FFF)
    temp /= 10.0

    humi = self._combine_bytes(data[2], data[3]) / 10.0

    return (temp, humi)

########################################################################################################################

def add_term(value, id_val, comment):
    query = """
    INSERT INTO
        test(j_value, id_value, comment)
    VALUES
        (%s,%s,%s)
    """

    values = (value, id_val, comment)
    cur.execute(query, values)
    print (value)
    print (id_val)
    print (comment)

########################################################################################################################
## COM PORT SELECTER
########################################################################################################################

# Start COM-Port Seting
try:
    parser = createParser()
    numComPort = parser.parse_args(sys.argv[1:])
    numPort = format(numComPort.name)
    if numPort == "1":
        #print ("++/dev/ttyACM"+format(namespace.name) )
        s_port='/dev/ttyACM'+numPort #format(numComPort.name)
        print (s_port )
    else:
        numPort = "0"
        s_port='/dev/ttyACM'+numPort #format(numComPort.name)
        print (s_port )

    ser = serial.Serial(
        #port='/dev/ttyACM0',
        port=s_port,
        baudrate=9600,
        timeout=10,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    ser.open()
    ser.isOpen()
    out =''
    if ser.isOpen():
        print("ebaniy port is OPEN")
        ser.write('F\r\n')
        while ser.inWaiting() > 0:
            out += ser.read(1)
        print(out)
    else:
        print("ebaniy port is CLOSE")
    # ser.close()
except IOError: # if port is already opened, close it and open it again and print message
    # ser.close()
    # ser.open()
    if ser.isOpen():
        print("ebaniy port is OPEN")
    else:
        print("ebaniy port is CLOSE")
    print(s_port)
    print ("port was already open, was closed and opened again!")


def openComPort(numPort):
    try:
        lnumPort = numPort
        # if numPort=="0":
        #     lnumPort = "1"
        # else:
        #     lnumPort = "0"

        s_port = '/dev/ttyACM' + lnumPort
        print(s_port)

        ser = serial.Serial(
            # port='/dev/ttyACM0',
            port=s_port,
            baudrate=9600,
            timeout=10,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

        ser.open()
        ser.isOpen()
        # ser.close()
    except IOError:  # if port is already opened, close it and open it again and print message
        #ser.close()
        #ser.open()
        print("port was already open, was closed and opened again!")



## END OF DECLARE
print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

## BEGIN PROGRAM
input=1
while 1 :
    # mylcd.lcd_display_string("Time: %s" %time.strftime("%H:%M:%S"), 1)
    mylcd.lcd_display_string(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), 2)

    print('=============================================')
    # get keyboard input
    #####################################################
    input = raw_input(">> ")
    if input == 'exit':
        ser.close()
        exit()

    #####################################################
    elif input == 'home':
        time.sleep(0.001)
        am2320 = AM2320(1)
        (t,h) = am2320.readSensor()
        print('{"num_sens": 0,"sens_type" : "AM2320", "sens_id" : "none","sens_Val": { "temp":'+str(t)+', "hum":'+str(h)+'}}')

    #####################################################
    elif input == 'a_term' and ser.isOpen():
        try:
            print ('{[')
            out = ''
            nums = ["0","1","2","3","4"]
            for i in nums: # ('0','1','2','3','4'):
                ser.write('R' + i + '\r\n')

                #time.sleep(1)
                while ser.inWaiting() > 0:
                    out += ser.read(1)

                if out != '':
                    print out
                if (i!=4):
                    # sys.stdout.write(',')
                    print (',')

            print (']}')

        except IOError:  # if port is already opened, close it and open it again and print message
            ser.open()
            print("port was already open, was closed and opened again!")

    #####################################################
    elif input == 'close':
        try:
            print ('{[')
            if ser.isOpen():
                print("Kakogo xuya port is OPEN")
                ser.close()
            else:
                print("port is CLOSED   do OPEN port")
                ser.open()
            print (']}')

        except IOError:  # if port is already opened, close it and open it again and print message
            #ser.open()
            print("port was already open, was closed and opened again!")

    #####################################################
    elif input == 'pg':
        withOutDelay = 1
        while 1 :
            mylcd.lcd_display_string(" M"+datetime.datetime.now().strftime("%m")+"D"+datetime.datetime.now().strftime("%d %H:%M:%S"), 2)
#            mylcd.lcd_display_string("D"+datetime.datetime.now().strftime("%m/%d %H:%M:%S"), 2)
            delta = datetime.datetime.now()-last_time_update
            #print(int(delta.seconds))
            #print( datetime.datetime.now())
            #print( last_time_update )

            #print('press space for abort')

            try:  # used try so that if user pressed other than the given key error will not be shown
                if keyboard.is_pressed('x'):  # if key 'a' is pressed
                    print('execution aborted')
                    break  # finishing the loop
                else:
                    pass
            except:
                break  # if user pressed other than the given key the loop will break

#            mylcd.lcd_display_string(datetime.datetime.now().strftime("%m/%d %H:%M:%s"), 2)

            if (lcdInf == 0) and((delta.seconds %5)==0):
                mylcd.lcd_display_string('H-> '+str(home_temp)+'C '+str(home_hum)+'%    ', 1)
                lcdInf = 1
                time.sleep(1)
            elif lcdInf == 1 and((delta.seconds %5)==0) :
#                try:
#                out = ''
#                ser.write('G\r\n')
#                time.sleep(1)
#                while ser.inWaiting() > 0:
#                    out += ser.read(1)
#                json_string = out
#                gdata = json.loads(json_string)
#                out = ''
#                except Exception:
#                    pass
#                    out = ''
                try:
                    mylcd.lcd_display_string('G-> '+str(gdata['sens_Val']['temp']) + 'C ' + str(gdata['sens_Val']['hum']) + '%    ', 1)
                except:
                    mylcd.lcd_display_string('G-> N/A C   N/A %   ',1)
                lcdInf =2
                time.sleep(1)
            elif lcdInf == 2 and((delta.seconds %5)==0):
                try:
                    mylcd.lcd_display_string('W-> ' + str(wdata['sens_Val']['volt']) + ' VOLT        ', 1)
                except:
                    mylcd.lcd_display_string('W->  N/A  VOLT          ',1)

                lcdInf = 0
                time.sleep(1)
                #
                try:
                    print('{[')
                    if ser.isOpen():
                        print("!COM PORT IS OPEN!")
                        print(datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")   )
                        #ser.close()
                        out =''
                        ser.write('H\r\n')
                        time.sleep(1.5)
                        while ser.inWaiting() > 0:
                            out += ser.read(1)
                        print(out)
                    else:
                        print("port is CLOSED   do OPEN port")
                        ser.open()
                    print(']}')

                    ser.write('F\r\n')
                    while ser.inWaiting() > 0:
                        out += ser.read(1)

                except IOError:  # if port is already opened, close it and open it again and print message
                    ser.close()
                    if numPort == "0":
                        numPort = "1"
                    else:
                        numPort = "0"
                    openComPort(numPort)
                    # ser.open()
                    print("port was already open, was closed and opened again!")

            # and  ser.isOpen()
            if ( delta.seconds>50 or withOutDelay == 1 ) :
                # ser.open()
                mylcd.lcd_display_string(" UPDATE ...     ", 2)
                withOutDelay = 0
                cur = conn.cursor()
                tmp_val='{['
                try:
                    nums = ["0","1","2","3","4"]
                    for i in nums:
                        out = ''
                        ser.write('R' + str(i) + '\r\n')
                        time.sleep(1.5)
                        while ser.inWaiting() > 0:
                            out += ser.read(1)
                        if out != '':
                            # print out
                            tmp_val+=out
                        if (i!="4"):
                            tmp_val+=','
                    # time.sleep(1)
                    tmp_val+=']}'
                    add_term(tmp_val,100,'from orangepi > a_term')
                except Exception:
                    tmp_val='{"num_sens": 0,"sens_type" : "DS18B20", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
                    add_term(tmp_val,-100,'from orangepi > a_term')
                    out = ''


                try:
                    if ser.isOpen():
                        try:
                            out = ''
                            ser.write('G\r\n')
                            time.sleep(2)
                            while ser.inWaiting() > 0:
                                out += ser.read(1)
                            #json_string = out
                            print(out)
                            gdata = json.loads(out) #json_string)
                            add_term(out,200,'from orangepi > G')
                        except Exception:
                            tmp_val='{"num_sens": 1,"sens_type" : "", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
                            add_term(tmp_val,-201,'from orangepi > G')
                except IOError:
                    #ser.open()
                    tmp_val='{"num_sens": 1,"sens_type" : "AM2320", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
                    add_term(out,-202,'from orangepi > G')
                except Exception:
                    tmp_val='{"num_sens": 0,"sens_type" : "", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
                    add_term(tmp_val,-203,'from orangepi > home')

                time.sleep(1)
                try:
                    time.sleep(0.5)
                    am2320 = AM2320(1)
                    time.sleep(1)
                    (t,h) = am2320.readSensor()
                    tmp_val='{"num_sens": 0,"sens_type" : "AM2320", "sens_id" : "none","sens_Val": { "temp":'+str(t)+', "hum":'+str(h)+'}}'
                    home_hum = h
                    home_temp = t
                    add_term(tmp_val,300,'from orangepi > home')
                except Exception:
                    tmp_val='{"num_sens": 0,"sens_type" : "", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
                    add_term(tmp_val,-300,'from orangepi > home')

                out=''
                try:
                    ser.write('W\r\n')
                    time.sleep(2)
                    while ser.inWaiting() > 0:
                        out += ser.read(1)
                    json_string = out
                    wdata = json.loads(json_string)
                    add_term(out,400,'from orangepi > W')
                except Exception:
                    tmp_val='{"num_sens": 1,"sens_type" : "WaterGrnd", "sens_id" : "none","sens_Val": { "volt": "N/A"}}'
                    add_term(tmp_val,-400,'from orangepi > W')

                #
                if gpio.input(port.PG7) != 1:
                    tmp_val='{"num_sens": 0,"sens_type" : "magnetic_switch", "sens_id" : "none","sens_Val": 1 }'
                    add_term(tmp_val,500,'from orangepi > magnetic_switch')
                else:
                    tmp_val='{"num_sens": 0,"sens_type" : "magnetic_switch", "sens_id" : "none","sens_Val": 0 }'
                    add_term(tmp_val,500,'from orangepi > magnetic_switch')
                #/

                try:
                    tFile = open("/sys/class/thermal/thermal_zone0/temp","r")
                    temp = float(tFile.readline())
                    tempC = temp/1000
                    #print ('{"num_sens":0, "sens_type":"CPU_temperature", "sens_id":"none", "sens_Val": { "temp":'+str(tempC)+'}}')
                    tFile.close()

                    tmp_val='{"num_sens":0, "sens_type":"CPU_temperature", "sens_id":"none",', ' "sens_Val": { "temp":'+str(tempC)+'}}'
                    add_term(tmp_val,600,'from orangepi > CPU_TEMPERATURE')

                    if tempC > 30:
                        gpio.output(port.PG8, gpio.HIGH) ## always on
                        #GPIO.output(17, 1)
                        gpio.output(port.PA7, gpio.LOW)
                        print "HOT"
                    else:
                        gpio.output(port.PG8, gpio.HIGH) ## always on
                        #GPIO.output(17, 0)
                        gpio.output(port.PA7, gpio.HIGH)
                        print "COLD"
                    lcdInf = 0
                except:
                    tFile.close()
                    tmp_val='{"num_sens":0, "sens_type":"CPU_temperature", "sens_id":"none", "sens_Val": { "temp":"N/A"}}'
                    add_term(tmp_val,-600,'from orangepi > CPU_TEMPERATURE')
                    #GPIO.cleanup()
                    #exit

#                if lcdInf == 0:
#                    mylcd.lcd_display_string('H-> '+str(home_temp)+'C '+str(home_hum)+'%    ', 1)
#                    lcdInf = 1
#                elif lcdInf == 1:
#                    mylcd.lcd_display_string('G-> '+str(gdata['sens_Val']['temp']) + 'C ' + str(gdata['sens_Val']['hum']) + '%    ', 1)
#                    lcdInf =2
#                elif lcdInf == 2:
#                    mylcd.lcd_display_string('*-> ' + str(home_temp) + 'C ' + str(home_hum) + '%    ', 1)
#                    lcdInf = 0
                time.sleep(1.5)
#                mylcd.lcd_display_string(datetime.datetime.now().strftime("%m/%d %H:%M:%S"), 2)
                conn.commit()
                cur.close()
                #time.sleep(45)
                last_time_update = datetime.datetime.now()
                # ser.close()
            else:
                time.sleep(1)
                # ser.open()

    else:
        out = ''
        while ser.inWaiting() > 0:
            out += ser.read(1)
        time.sleep(1)
        ser.write(input + '\r\n')

        # let's wait one second before reading output (let's give device time to answer)
        #time.sleep(1)
        while ser.inWaiting() > 0:
            out += ser.read(1)
            
        if out != '':
            print out

