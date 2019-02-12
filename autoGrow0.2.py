
## 
import datetime
import smbus
import time

## for color text
from termcolor import colored

#GPIO
import RPi.GPIO as GPIO

import RPi_I2C_driver

## For clear consol
import os

## for AM2320
import posix
from fcntl import ioctl
from datetime import datetime

## For serial
import serial

## For Json
import json


## GPIO INIT
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
##########################
## Big Relay module
GPIO.setup(26, GPIO.OUT)  
GPIO.output(26, True)   ## INIT TO OFF
GPIO.setup(19, GPIO.OUT) 
GPIO.output(19, True)   ## INIT TO OFF
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, True)   ## INIT TO OFF
GPIO.setup(6, GPIO.OUT)
GPIO.output(6, True)   ## INIT TO OFF
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, True)   ## INIT TO OFF
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, True)   ## INIT TO OFF
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, True)   ## INIT TO OFF
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, True)   ## INIT TO OFF
########################
## This is smal relay module/ USE INVERT VALUE 
GPIO.setup(18, GPIO.OUT)  
GPIO.output(18, True)        ## INIT TO ON   # Cooller in MainBox
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, False)   ## INIT TO OFF
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, False)   ## INIT TO OFF
## Magnet Soid TEST Pin
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

now = datetime.now()

########################
## FOR AM2320
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
  
    # wake AM2320 up, goes to sleep to not warm up and affect the humidity sensor 
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
## COM PORT SELECTER
########################################################################################################################
def openComPort(numPort, command="H"):
  lnumPort = numPort
  s_port = '/dev/ttyACM' + str(lnumPort)
  ##print(s_port)
  ser = serial.Serial(
              port=s_port,
              baudrate=9600,
              timeout=10,
              parity=serial.PARITY_NONE,
              stopbits=serial.STOPBITS_ONE,
              bytesize=serial.EIGHTBITS
          )
  try:
    if ser.isOpen()== True :
       ser.close()
       ser.open()
      
    if ser.isOpen():
      ser.write('?\r\n')
      time.sleep(2)
      out = ''
      while ser.inWaiting() > 0:
        out += ser.read(1)
  
      ser.write(command+'\r\n')
      time.sleep(3)
      out = ''
      while ser.inWaiting() > 0:
        out += ser.read(1)            
    if ser.isOpen()== True :
       ser.close()
    return out 
  except:
    return "{\"Error\":\"Com-port Error\"}"
##  finally:
##    return "{\"Error\":\"Com-port Error\"}"  
 

class SensorAM2320:
  name = 'sensor am2320'
  temperature = -85.5
  humidity = - 99.9
  prTemperature = -85.5
  prHumidity = - 99.9
  lastUpdate = datetime.now()
  lastUpdateSec = -1
  temperatureMove = "None"
  humidityMove = "None"

  def __init__(self, arg0="sensor am2320", arg1=-85.5, agr2=-99.9):
    self.name=arg0
    self.temperature = arg1
    self.humidity = agr2

  def setValue(self, arg0, arg1):
    # print("setValue   arg0:"+str(arg0)+" prTemperature:"+str(self.prTemperature)+"           arg1:"+str(arg1)+"    prHumidity:"+str(self.prHumidity))
    if arg0 > self.prTemperature:
      self.temperatureMove=  u'\u25b2'
    elif arg0 < self.prTemperature:
      self.temperatureMove = u'\u25bc'
    elif arg0 == self.prTemperature:
      self.temperatureMove = u'\u25CF'

    # print(self.temperatureMove)

    if arg1 > self.prHumidity:
      self.humidityMove=  u'\u25b2'
    elif arg1 < self.prHumidity:
      self.humidityMove = u'\u25bc'
    elif arg1 == self.prHumidity:
      self.humidityMove = u'\u25CF'

    # print(self.humidityMove)

    self.prTemperature = self.temperature
    self.prHumidity = self.humidity
    self.temperature = arg0
    self.humidity = arg1
    self.lastUpdate = datetime.now()
    self.lastUpdateSec =  datetime.now() - self.lastUpdate

  def setName(self, arg0):
    self.name=arg0

  def getValue(self) :
    return (self.temperature, self.humidity)

  def printValue(self) :
    print (self.temperature)
    print (self.humidity)
    #return (self.temperature, self.humidity)

  def printf(self): 
    delta = datetime.now() - self.lastUpdate 
    print ("Sensor name: " + self.name + "   Last Update:" + str(self.lastUpdate) + "  At seconds:  "+ str(self.delta) )
    print ("Sensor name: " + self.name + "   Temperature: " + str(self.temperature)+ "C" + self.temperatureMove +"  Humidity: " + str(self.humidity)+ "%"  + self.humidityMove)

  def printfc(self):
    termColor = 'white'
    humColor = 'white'
    if self.temperature <= 18:
      termColor = 'blue'
    elif self.temperature > 18 and self.temperature <= 24:
      termColor = 'cyan'
    elif self.temperature > 24 and self.temperature <= 29:
      termColor = 'green'
    elif self.temperature > 29 and self.temperature <= 33:
      termColor = 'yellow'
    elif self.temperature > 33 :
      termColor = 'red'
    else:
      termColor = 'red'

    if self.humidity <= 40:
      humColor = 'red'
    elif self.humidity > 40 and self.humidity <= 60:
      humColor = 'green'
    elif self.humidity > 60 :
      humColor = 'yellow'
    else:
      humColor = 'red'

    delta = datetime.now() - self.lastUpdate
    if delta.seconds<60:
      timeColor = 'green'
    elif delta.seconds>=60 and delta.seconds<120:
      timeColor = 'yellow'
    elif delta.seconds>=60 and delta.seconds<16:
      timeColor = 'green'
    else:
      timeColor = 'red'


    print ("Sensor name: " + self.name + "   Last Update:" + str(self.lastUpdate) + "  At seconds:  "+ colored(str(delta.seconds),timeColor))
    print ("Sensor name: " + self.name + "   Temperature: " + colored(str(self.temperature),termColor)+ "C "+ self.temperatureMove+"  Humidity: " + colored(str(self.humidity),humColor)+ "%" + self.humidityMove)
    
##    print("Time update temperature & humidity: " + str(self.sensHome.lastUpdate) )
##    print (colored("HOME TEMPERATURE :" ,'white')+ colored(str(self.sensHome.temperature)+'C ', termColor) +  colored("HOME HUMIDITY :", 'white') + colored(str(self.sensHome.humidity)+'%', humColor))
    

class HomeAM2320(SensorAM2320):
  def readValue(self):      ## Read sensor value
    #print("home sensor readValue")
    try:
      am2320 = AM2320(1)
      (t,h) = am2320.readSensor()
      #print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
      #print("t="+str(t))
      #print("h=" + str(h))
      self.setValue(t,h)
      self.lastUpdate = datetime.now()
      time.sleep(5)
    except:
      self.setValue(-1,-1)

  def __init__(self, arg0="sensor am2320", arg1=-85.5, agr2=-99.9):
    self.name=arg0
    if arg1<0 or arg2<0 :
      self.readValue()
    else:
      self.temperature = arg1
      self.humidity = agr2

  def update(self):
    #print("start update Home sens")
    self.readValue()

class BoxAM2320(SensorAM2320):
  boxSensValue = "{}"
  def readValue(self):
    try:
      self.boxSensValue = openComPort(0, command="G")
      data = json.loads(self.boxSensValue)
      self.setValue(data["sens_Val"]['temp'],data["sens_Val"]['hum'])
    except:
      print("Error parsignj JSON  = ")
      print(self.boxSensValue)

  def __init__(self, arg0="sensor am2320", arg1=-85.5, agr2=-99.9):
    self.name = arg0
    if arg1<0 or arg2<0 :
      self.readValue()

  def update(self):
    self.readValue()       

class TemperatureSensor:
  name = 'sensor am2320'
  sensor_addres = "FFFFFFFFFFFF"
  comment = "comment about this sensor"
  temperatureC = -85.5
  temperatureF = -85.5
  prTemperatureC = -85.5
  prTemperatureF = -85.5
  lastUpdate = datetime.now()
  prLastUpdate = datetime.now()
  lastJson = ""
  numSens = 0
  temperatureMove ="none"

  def __init__(self, numSens=0, sensor_addres="00:00:00:00:00:00:00:00", temperatureC = -77, temperatureF = -77):
    self.numSens = numSens
    print("install sensor " + str(self.numSens))
    self.name = "DS18B20__" + str(self.numSens)
    self.sensor_addres = sensor_addres
    self.temperatureC = temperatureC
    self.temperatureF = temperatureF
    self.lastUpdate = datetime.now()
    if temperatureC < 0 or temperatureF < 0 :
      self.setValue()

  def __repr__(self):
    delta = datetime.now() - self.lastUpdate
    return '<TemperatureSensor (temperatureC={}, prTemperatureC={}, name ={}, sensor_addres={}), lastUpdate={}, lastSecondAgo={}>'.format(self.temperatureC, self.prTemperatureC, self.name, self.sensor_addres,self.lastUpdate, str(delta.seconds))


  def setName(self, name):
    self.name=name

  def setComment(self, comment):
    self.comment=comment

  def setValue(self, comPort = 0):

    # print ("***************************   R"+str(self.numSens))
    # print (self.lastJson)

    try:
      self.lastJson = openComPort(comPort, command="R" + str(self.numSens))
      data = json.loads(self.lastJson)
      self.prTemperatureC=self.temperatureC
      self.prTemperatureF=self.temperatureF
      self.temperatureC = data["sensors"][0]["temperatuteC"]
      self.temperatureF = data["sensors"][0]["temperatuteF"]

      if self.temperatureC > self.prTemperatureC:
        self.temperatureMove=  u'\u25b2     '
      elif self.temperatureC < self.prTemperatureC:
        self.temperatureMove = u'\u25bc   '
      elif self.temperatureC == self.prTemperatureC:
        self.temperatureMove = u'\u25CF   '

      #print("======================================")
      #print(data["sensors"][0])

      self.sensor_addres = data["sensors"][0]["sensor_addres"]
      #self.name = name
      self.prLastUpdate = self.lastUpdate
      self.lastUpdate = datetime.now()

    except:
      print(" if This Error - its critical. Can't found first sensor [NEED remove this excep on hard on vervion 1.1]")
      print("I get it :"+self.lastJson)

  def updateOld(self, seconds = 60):
    delta = datetime.now() - self.lastUpdate
    if delta.seconds > seconds:
      # print ("Object is olded - UPDATE HIM")
      self.setValue()
    # else:
    #   print ("Yang Object GO Out!")
  def updateValue(self):
    self.setValue()


  def getValueC(self):
    return (self.temperatureC , self.prTemperatureC)

  def getValueF(self):
    return (self.temperatureF , self.prTemperatureF)

  ### return formated temperature
  def getValueFF(self):
    val = u''
    if self.temperatureC>self.prTemperatureC:
        moviVal = u'\u25B2'
    elif self.temperatureC<self.prTemperatureC:
        moviVal = u'\u25BC'
    elif self.temperatureC==self.prTemperatureC:
        moviVal = u'\u25CF'
    val = str(self.temperatureC)+u'C\u25e6'+moviVal
    return val.ljust(5)


  def printValue(self):
    print (self.temperatureC)
    # return (self.temperature, self.humidity)

  def printf(self):
    delta = datetime.now() - self.lastUpdate
    print ("Sensor name: " + self.name + "   Last Update:" + str(self.lastUpdate) + "  At seconds:  " + str(delta.seconds) + "  move:" + self.temperatureMove)
    print ("Sensor name: " + self.name + "   Temperature: " + str(self.temperatureC) + "C    Temperature: " + str(self.temperature) + "F   Humidity: ")

  def getColor(self, value=1, arg0=1, arg1=1):
      if value < arg0:
        return "green"
      elif value >= arg0 and value < arg1:
        return "yellow"
      elif value >= arg1:
        return "red"
      else:
        return "red"


  def printfc(self,colorWarning=35,colorAlarm=40):
    termColor = 'white'
    termColor = self.getColor(self.temperatureC,colorWarning,colorAlarm)

    prTermColor = 'white'
    prTermColor = self.getColor(self.prTemperatureC, colorWarning, colorAlarm)

    delta = datetime.now() - self.lastUpdate
    if delta.seconds < 60:
      timeColor = 'green'
    elif delta.seconds >= 60 and delta.seconds < 120:
      timeColor = 'yellow'
    elif delta.seconds >= 60 and delta.seconds < 16:
      timeColor = 'green'
    else:
      timeColor = 'red'

    print ("Sensor name: " + self.name + "   Last Update:" + str(self.lastUpdate) + "  At seconds:  " + colored(str(delta.seconds), timeColor))
    print ("Sensor name: " + self.name + "   Temperature: " + colored(str(self.prTemperatureC),prTermColor) + "C -> "  + colored(str(self.temperatureC),termColor) + "C " + self.temperatureMove )

class BoxClimate:
  name = "MainBox"
  sensHome = HomeAM2320("Home")
  sensBox = BoxAM2320("Box ")
  obj = TemperatureSensor()
  ##print(obj)
  sensArrayXXX = []
  countSensor = 0  ## type: Any

  magneticSwitchStatus = 0
  lastState = 0
  lastReadState = datetime.now()
  timeStartDay = now.replace(hour=8, minute=00, second=0, microsecond=0)
  timeEndDay = now.replace(hour=22, minute=00, second=0, microsecond=0)
  lastTermHumHomeUpd = datetime.now()
  needState = 0
  colorText = 'green'

  unitNeedState = {-1: "NEED NIGHT",
                   0: "FAILURE ERROR is not avalible state",
                   1: "NEED DAY"}

  unitLampState = {-1: "LAMP IS OFF",
                   0: "FAILURE ERROR is not avalible lamp status",
                   1: "LAMP IS ON"}

  def updateSensors(self):
    if self.countSensor == 0:
      self.setCountSensors()
    for x in range(0,self.countSensor):
      self.updateSensor(x)

  def updateOldSensors(self, seconds):
    if self.countSensor == 0:
      self.setCountSensors()
    for x in range(0,self.countSensor):
      self.updateOldSensor(x,seconds)

  def updateSensor(self, sensNumber):
    obj = self.sensArrayXXX[sensNumber]
    obj.updateValue()
    self.sensArrayXXX[sensNumber]=obj

  def updateOldSensor(self, sensNumber, seconds):
    obj = self.sensArrayXXX[sensNumber]
    obj.updateOld(seconds)
    self.sensArrayXXX[sensNumber]=obj

  def initSensors(self):
    self.setCountSensors()
    for x in range(0, self.countSensor):
      obj = TemperatureSensor(int(x))
      self.sensArrayXXX.append(obj)

  def setCountSensors(self, comPort = 0):
    try:
      self.sensArray = openComPort(comPort, command="R")
      data = json.loads(self.sensArray)
      self.countSensor = data["sens_count"]
      ##return self.countSensor
    except:
      print("Error on parsing json" + self.sensArray)

  def getSensors(self,colorWarning=35,colorAlarm=40):
    for x in range(0, self.countSensor):
      self.getSensor(x,colorWarning,colorAlarm)

  def getSensor(self, sensNumber=0,colorWarning=35,colorAlarm=40):
    print (str(sensNumber+1)+"/"+str(self.countSensor))
    self.sensArrayXXX[sensNumber].printfc(colorWarning,colorAlarm)
    # obj = self.sensArrayXXX[sensNumber]
    # print obj
    # obj.
    time.sleep(1)
    # except:
    #   print("object array list error 387 ")
    
  def __init__(self, arg0):
    self.name=arg0
    print(" INIT OBJECT "+ self.name +"  => Class: "+ self.name +" Created")
    now = datetime.now()
    if now > self.timeStartDay and now < self.timeEndDay:
      self.needState = 1
      print(" INIT OBJECT "+ self.name +"  => need Status => 1  [NEED DAY]")
    else:
      self.needState = -1
      print(" INIT OBJECT "+ self.name +"  => need Status => -1  [NEED NIGHT]")

    print(" INIT OBJECT "+ self.name +"  => Test lamp (HP0 connector)... ")

    self.getMagneticSwitchStatus()
    self.lastReadState = datetime.now()
    time.sleep(5)

  def getColor(self, value=1,  arg0 = 1, arg1 = 1):
    if value<arg0:
      return "green"
    elif value>arg0 and value<arg1:
      return "yellow"
    elif value>arg1:
      return "red"

  def setNeedState(self):
    print("Test lamp (HP0 connector)... ")
    now = datetime.now()
    if now > self.timeStartDay and now < self.timeEndDay:
      self.needState = 1
    else:
      self.needState = -1
    print("needState= > " + str(self.needState))
    time.sleep(7)
    
  def getMagneticSwitchStatus(self):
    input_state = GPIO.input(25)
    if input_state == False:
      print colored('Get magnetig Switch status IS ON', 'green')
      self.magneticSwitchStatus = 1
      self.lastState = 1
    else:
      print colored('Get magnetig Switch status IS OFF', 'green')
      self.magneticSwitchStatus = -1
      self.lastState = -1

  def getColorText(self):
    if self.lastState == self.needState and self.needState!=0:
      return 'green'
    else:
      return 'red'  

  def setState(self):
    self.setNeedState()
    now = datetime.now()
    input_state = GPIO.input(25)      
    print("Test lamp (HP0 connector)... ")
    if input_state == False:
      self.lastState = 1
    else:
      self.lastState = -1
    self.lastReadState = datetime.now()

    if self.lastState == self.needState:
      colorText = 'green'
    else:
      colorText = 'red'

    if self.lastState == 1:
      print colored('OBJECT' +self.name+'   LAMP IS ON ',colorText)
    elif self.lastState == -1:
      print colored('OBJECT' +self.name+'   LAMP IS OFF ',colorText)
    else:
      print colored('OBJECT' +self.name+'  Can''t read lamp state  ','red')
    time.sleep(5)

  def getInfo(self):
    print("===============================================")
    print(datetime.now()) # Print Date
    print("===============================================")
    print colored("Time update status: " + str(self.lastReadState) + "STATUS: " + self.unitNeedState[self.needState] + " NOW: " + self.unitLampState[self.lastState], self.getColorText())
    self.getTermHumHome
    time.sleep(5)

  def getSensInfo(self):
    print("===============================================")
    print(datetime.now()) # Print Date
    print("===============================================")
    print("TEMPERATURE " +self.sensHome.temperature  )
    print("humidity " +self.sensHome.humidity  )    
    print colored("Time update status: " + str(self.lastReadState) + "STATUS: " + self.unitNeedState[self.needState] + " NOW: " + self.unitLampState[self.lastState], self.getColorText())
    self.setTermHumHome
    time.sleep(5)    

  def setTermHumHome(self):
    #try:
      am2320 = AM2320(1)
      (t,h) = am2320.readSensor()
      print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
      self.sensHome.setValue(t,h)
      self.sensHome.lastUpdate = datetime.now()
      self.getTermHumHome()
    #except:
    #  print colored("ERROR READ AM2320 HOME-sensor", 'red')
    #  self.sensHome.temperature = -85.5
    #  self.sensHome.humidity = -99.9
    
  def getTermHumHome(self):
    termColor = 'white'
    humColor = 'white'
    if self.sensHome.temperature <= 18:
      termColor = 'blue'
    elif self.sensHome.temperature > 18 and self.sensHome.temperature <= 24:
      termColor = 'cyan'
    elif self.sensHome.temperature > 24 and self.sensHome.temperature <= 29:
      termColor = 'green'
    elif self.sensHome.temperature > 29 and self.sensHome.temperature <= 33:
      termColor = 'yellow'
    elif self.sensHome.temperature > 33 :
      termColor = 'red'
    else:
      termColor = 'red'

    if self.sensHome.humidity <= 40:
      humColor = 'red'
    elif self.sensHome.humidity > 40 and self.sensHome.humidity <= 60:
      humColor = 'green'
    elif self.sensHome.humidity > 60 :
      humColor = 'yellow'
    else:
      humColor = 'red'
    print("Time update temperature & humidity: " + str(self.sensHome.lastUpdate) )
    print (colored("HOME TEMPERATURE :" ,'white')+ colored(str(self.sensHome.temperature)+'C ', termColor) +  colored("HOME HUMIDITY :", 'white') + colored(str(self.sensHome.humidity)+'%', humColor))



      
#print(now) # 38

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
  print ("==========    START MAIN    ===============")
  fontdata1 = [
    [0b00000,
     0b00111,
     0b01000,
     0b11010,
     0b10101,
     0b01000,
     0b00111,
     0b00000],

    [0b00100,
     0b11111,
     0b00000,
     0b10101,
     0b01010,
     0b00000,
     0b11111,
     0b00000],

    [0b01100,
     0b11111,
     0b00110,
     0b11111,
     0b11111,
     0b00110,
     0b11111,
     0b01100],

    [0b00110,
     0b00110,
     0b01100,
     0b01100,
     0b11000,
     0b11000,
     0b10000,
     0b10000],

    [0b10001,
     0b10001,
     0b10001,
     0b10001,
     0b10001,
     0b10001,
     0b10001,
     0b10001],

    [0b01100,
     0b01100,
     0b00110,
     0b00110,
     0b00011,
     0b00011,
     0b00001,
     0b00001],

  ]

  fontdata2 = [
    [0b11111,
     0b11000,
     0b10111,
     0b00101,
     0b01010,
     0b10111,
     0b11000,
     0b11111],

    [0b11111,
     0b00000,
     0b11111,
     0b01010,
     0b10101,
     0b11111,
     0b00000,
     0b11111],

    [0b11111,
     0b01101,
     0b00101,
     0b10111,
     0b01111,
     0b00101,
     0b01101,
     0b11111],

    [0b11101,
     0b11111,
     0b11111,
     0b11111,
     0b11111,
     0b01111,
     0b11111,
     0b11111],

    [0b11111,
     0b01011,
     0b10111,
     0b01011,
     0b11111,
     0b11111,
     0b11111,
     0b11101],

    [0b11111,
     0b11111,
     0b11101,
     0b11111,
     0b11111,
     0b11111,
     0b10111,
     0b11111],

  ]
  print ("==========    Create main class    ===============")
  mainBox = BoxClimate("mainBox")
  print ("==========    Init Sensosrs    ===============")
  mainBox.initSensors()

  while True:
    #cls()
    mainBox.sensBox.update()
    mainBox.sensHome.update()
    cls()
    print ("==========    START While    ===============")
    now = datetime.now()
    ## if pora to update

    mainBox.sensHome.printfc()
    mainBox.sensBox.printfc()
########    #mainBox.getSensors()

    # print mainBox.sensArrayXXX[0]

    #
    # mainBox.updateSensors()
    # mainBox.getSensor(0)
    # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # mainBox.updateSensors()
    # mainBox.getSensors()
    print("@@@@@@   Box humidity control   @@@@@")

    if mainBox.sensBox.humidity<45:
        print(" Filter, cerculation FAN is OFF  is dry, less 45% now humidity =" + str(mainBox.sensBox.humidity))
        GPIO.output(6, True)
    elif mainBox.sensBox.humidity>55:
        print(" Filter, cerculation FAN is  ON  is wet, more 55% now humidity =" + str(mainBox.sensBox.humidity))
        GPIO.output(6, False)
    else:
        print(" Filter, cerculation FAN is  ON  is wet, more 55% now humidity =" + str(mainBox.sensBox.humidity))

    print("##########################################################################")
    print("########################     LAMP HEALTH    ##############################")
    print("##########################################################################")
    print("")
    print(u'|\u25BC\u25BC\u25BC\u25BC\u25BC\u25BC\u25BC\u25BC\u25BC\u25BC\u25BC\u25BC|   \u2551\u2551 \u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557         |\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2\u25B2|')
    print(u'|\u25BC  IN AIR  \u25BC|   \u2551\u2551 \u2551\u2588\u2588\u2588\u2588\u2588 THROTTLE 250W \u2588 ON  \u2588\u2551         |\u25B2  OUT AIR  \u25B2|')
    print(u'|\u25BC '+colored(mainBox.sensArrayXXX[1].getValueFF() ,color=mainBox.getColor(mainBox.sensArrayXXX[1].temperatureC, 30, 40)) + u' \u25BC|   \u2551\u255a\u2550\u2551\u25baIN  \u2588\u2588   '+colored(str(mainBox.sensArrayXXX[2].temperatureC).ljust(5),color=mainBox.getColor(mainBox.sensArrayXXX[4].temperatureC, 50, 60)) + u'C\u00ba\u25B2  \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551         |\u25B2           \u25B2|')
    print(u'|\u2588          \u2588|   \u2551  \u2551220V \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588 OUT\u25ba\u2551\u2550\u2550\u2550\u2550\u2550\u2550\u2557  |\u2588           \u2588|')
    print(u'|\u2588\u25BC   IN   \u25BC\u2588|   \u255a\u2550\u2550\u2551\u25baIN  \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588 OUT\u25ba\u2551\u2550\u2550\u2550\u2550\u2550\u2557\u255a\u2550\u25BA|\u2588\u25B2\u25B2  OUT  \u25B2\u25B2\u2588|')
    print(u'|\u2588 '+colored(str(mainBox.sensArrayXXX[3].temperatureC),color=mainBox.getColor(mainBox.sensArrayXXX[3].temperatureC, 30, 40)) + u'C\u00ba\u25BC \u2588|      \u255A\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d     \u255a\u2550\u2550\u25Ba|\u2588 '+colored(str(mainBox.sensArrayXXX[4].temperatureC).ljust(5),color=mainBox.getColor(mainBox.sensArrayXXX[4].temperatureC, 30, 40)) + u'C\u00ba\u25B2  \u2588|')

    print(u'|\u2588           \u2588\\\u2553\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2556/\u2588            \u2588|')
    print(u'|\u2588            \u2588\u2551     ___________________________________\u2551\u2588             \u2588|')
    print(u'|\u2588             \u2551 \u25BA  /  \u2554\u2550\u263c\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u263c\u2550\u2550\u2560\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557   \u2588|')
    print(u'|\u2588             \u2551 \u25BA (   \u255a\u2550'+ colored(u'\u2591\u2592\u2593\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2593\u2592\u2591','yellow') + u'\u2550\u2550\u2551 '+colored(str(mainBox.sensArrayXXX[0].temperatureC).ljust(5),color=mainBox.getColor(mainBox.sensArrayXXX[0].temperatureC, 30, 40)) + u'C\u00ba\u25B2 \u2551   \u2588|')
    print(u' \\\u2588            \u2551 \u25BA  \___________________________________\u2560\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255D  \u2588/ ')
    print(u'  \\\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551                                        \u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588/  ')
    print(u'               \u2559\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u255c')
    print("")
    print("##########################################################################")
    # print (mainBox.sensArrayXXX[0].temperatureC)
    mainBox.updateOldSensors(60) ## update older 120 seconds
    time.sleep(5)



if __name__ == '__main__':
  cls()
  timeOn = now.replace(hour=8, minute=00, second=0, microsecond=0)
  timeOff = now.replace(hour=22, minute=00, second=0, microsecond=0)

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    pass
    #lcd_byte(0x01, LCD_CMD)
