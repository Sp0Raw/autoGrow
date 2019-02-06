
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

# Start COM-Port Seting
##try:
##    parser = createParser()
##    numComPort = parser.parse_args(sys.argv[1:])
##    numPort = format(numComPort.name)
##    if numPort == "1":
##        #print ("++/dev/ttyACM"+format(namespace.name) )
##        s_port='/dev/ttyACM'+numPort #format(numComPort.name)
##        print (s_port )
##    else:
##        numPort = "0"
##        s_port='/dev/ttyACM'+numPort #format(numComPort.name)
##        print (s_port )
##
##    ser = serial.Serial(
##        #port='/dev/ttyACM0',
##        port=s_port,
##        baudrate=9600,
##        timeout=10,
##        parity=serial.PARITY_NONE,
##        stopbits=serial.STOPBITS_ONE,
##        bytesize=serial.EIGHTBITS
##    )
##
##    ser.open()
##    ser.isOpen()
##    out =''
##    if ser.isOpen():
##        print("ebaniy port is OPEN")
##        ser.write('F\r\n')
##        while ser.inWaiting() > 0:
##            out += ser.read(1)
##        print(out)
##    else:
##        print("ebaniy port is CLOSE")
##    # ser.close()
##except IOError: # if port is already opened, close it and open it again and print message
##    # ser.close()
##    # ser.open()
##    if ser.isOpen():
##        print("ebaniy port is OPEN")
##    else:
##        print("ebaniy port is CLOSE")
##    print(s_port)
##    print ("port was already open, was closed and opened again!")




     

  
  
#### Variable need replace it in cfg
lampCooling=1

class SensorAM2320:
  name = 'sensor am2320'
  temperature = -85.5
  humidity = - 99.9
  lastUpdate = datetime.now()

  def __init__(self, arg0="sensor am2320", arg1=-85.5, agr2=-99.9):
    
    self.name=arg0
    self.temperature = arg1
    self.humidity = agr2
    print(" Created Object "+ arg0)
    time.sleep(1)

  def setValue(self, arg0, arg1):
    self.temperature = arg0
    self.humidity = arg1
    self.lastUpdate = datetime.now()

  def setName(self, arg0):
    self.name=arg0

  def getValue(self) :
    return (self.temperature, self.humidity)

  def printValue(self) :
    print (self.temperature)
    print (self.humidity)
    #return (self.temperature, self.humidity)
  
    

class BoxClimate:
  name = "MainBox"
  sensHome = SensorAM2320("Home")
  #sensHome.printValue()
  temperatureBox = -85.5
  humidityBox = 99.9
  
  magneticSwitchStatus = 0
  lastState = 0
  lastReadState = datetime.now()
  timeStartDay = now.replace(hour=8, minute=00, second=0, microsecond=0)
  timeEndDay = now.replace(hour=22, minute=00, second=0, microsecond=0)
  lastTermHumHomeUpd = datetime.now()
  needState = 0
  colorText = 'green'

  unitNeedState = {-1 : "NEED NIGHT",
                    0 : "FAILURE ERROR is not avalible state",
                    1 : "NEED DAY"}

  unitLampState = {-1 : "LAMP IS OFF",
                    0 : "FAILURE ERROR is not avalible lamp status",
                    1 : "LAMP IS ON"}  
  
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
      
  def setNeedState(self):
    print("Test lamp (HP0 connector)... ")
    now = datetime.now()
    if now > self.timeStartDay and now < self.timeEndDay:
      self.needState = 1
    else:
      self.needState = -1
    print("needState= > " + str(self.needState))
    time.sleep(7)
    
  def printx(self):
    print("asdfasdfasdf asdf asdf asdf asd fas df asd")

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

  #def set
  def openComPort(self, numPort, command="S"):
      lnumPort = numPort
      s_port = '/dev/ttyACM' + str(lnumPort)
      #print(s_port)
      ser = serial.Serial(
              port=s_port,
              baudrate=9600,
              timeout=10,
              parity=serial.PARITY_NONE,
              stopbits=serial.STOPBITS_ONE,
              bytesize=serial.EIGHTBITS
          )
    #try:
      if ser.isOpen()== True :
         ser.close()
         ser.open()
      
      #try:
      if ser.isOpen():
          ser.write('?\r\n')
          time.sleep(1)
          out = ''
          while ser.inWaiting() > 0:
            out += ser.read(1)
          ser.write(command+'\r\n')
          time.sleep(1)
          out = ''
          while ser.inWaiting() > 0:
            out += ser.read(1)            
          print(out)
##              gdata = json.loads(out) #json_string)
##                #add_term(out,200,'from orangepi > G')
##              try:
##                    mylcd.lcd_display_string('W-> ' + str(wdata['sens_Val']['volt']) + ' VOLT        ', 1)
###!                 except:
###!                    mylcd.lcd_display_string('W->  N/A  VOLT          ',1)
##              except Exception:
##                tmp_val='{"num_sens": 1,"sens_type" : "", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
##                #add_term(tmp_val,-201,'from orangepi > G')
          
            #ser.open()
          #tmp_val='{"num_sens": 1,"sens_type" : "AM2320", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
            #add_term(out,-202,'from orangepi > G')
      #except Exception:
        #tmp_val='{"num_sens": 0,"sens_type" : "", "sens_id" : "none","sens_Val": { "temp":"N/A", "hum":"N/A"}}'
        #add_term(tmp_val,-203,'from orangepi > home')   

        # ser.close()
        #ser.close()
    
        #return out
      ser.close()
    #except IOError:  # if port is already opened, close it and open it again and print message
      #ser.close()
      #ser.open()
      #print("port was already open, was closed and opened again!")

      
print(now) # 38

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
  mainBox = BoxClimate("mainBox")
##  input_state = GPIO.input(25)      
##  print("Test lamp  H0 ... ")
##  if input_state == False:
####          lastTimeLampOn = datetime.datetime.now()
##          print colored('LAMP IS ON', 'green')
##          time.sleep(7)
##          ## It's Ok !
##          ##
##        else:
##          print colored('LAMP IS OFF', 'red')
##          time.sleep(2)
##          lNow = datetime.datetime.now()
##          deltaTime = lNow - lastTimeLampOn
##          print (deltaTime)
##          duration_in_s = deltaTime.total_seconds()
##          minutes = divmod(duration_in_s, 60)[0] 
##          print (minutes)
##          if minutes>=lampCooling:
##            GPIO.output(19, False)
##            time.sleep(1)  
  
  lastTimeLampOn = datetime.now()
  lastTimeLampOff = datetime.now()
  lastTurnOff = datetime.now()
  lNow = datetime.now()
  lastComRead = datetime.now()
  timesOfDay =0
  lampStat   =0
  mylcd = RPi_I2C_driver.lcd()
  fontdata1 = [      
        [ 0b00000, 
          0b00111, 
          0b01000,
          0b11010,
          0b10101, 
          0b01000, 
          0b00111, 
          0b00000],


        [ 0b00100, 
          0b11111, 
          0b00000,
          0b10101,
          0b01010, 
          0b00000, 
          0b11111, 
          0b00000],

        [ 0b01100, 
          0b11111, 
          0b00110,
          0b11111,
          0b11111, 
          0b00110, 
          0b11111, 
          0b01100 ],
        
        [ 0b00110, 
          0b00110, 
          0b01100,
          0b01100,
          0b11000, 
          0b11000, 
          0b10000, 
          0b10000],

        [ 0b10001, 
          0b10001, 
          0b10001,
          0b10001,
          0b10001, 
          0b10001, 
          0b10001, 
          0b10001],

        [ 0b01100, 
          0b01100, 
          0b00110,
          0b00110,
          0b00011, 
          0b00011, 
          0b00001, 
          0b00001],

      ]

  fontdata2 = [      
        [ 0b11111, 
          0b11000, 
          0b10111,
          0b00101,
          0b01010, 
          0b10111, 
          0b11000, 
          0b11111],

        [ 0b11111, 
          0b00000, 
          0b11111,
          0b01010,
          0b10101, 
          0b11111, 
          0b00000, 
          0b11111],

        [ 0b11111, 
          0b01101, 
          0b00101,
          0b10111,
          0b01111, 
          0b00101, 
          0b01101, 
          0b11111 ],
        
        [ 0b11101, 
          0b11111, 
          0b11111,
          0b11111,
          0b11111, 
          0b01111, 
          0b11111, 
          0b11111],

        [ 0b11111, 
          0b01011, 
          0b10111,
          0b01011,
          0b11111, 
          0b11111, 
          0b11111, 
          0b11101],

        [ 0b11111, 
          0b11111, 
          0b11101,
          0b11111,
          0b11111, 
          0b11111, 
          0b10111, 
          0b11111],

      ] 

  while True:
    now = datetime.now()
    
  
    ## this is main loop
    if now > timeOn and now < timeOff: # DAY
      now = datetime.now()
      #

      LampOn = now - lastTimeLampOn  
      deltaTime = now - lNow
      cls()
      print("DAY " + datetime.now().strftime("%Y/%m/%d %H:%M:%S")+ "    delta "+ str( 31- deltaTime.seconds))
      input_state = GPIO.input(25)
      if input_state == False:
        print colored('LAMP IS ON', 'green')
      else:
        print colored('LAMP IS OFF', 'red')
      print ("   "+str(LampOn))
      duration_in_s = deltaTime.total_seconds()
      minutes = divmod(duration_in_s, 60)[0] 
      print ("  LAMP IS ON " + str(minutes) + "minutes")

      print("############" + mainBox.name + "############")
      mainBox.getInfo()
 
   
      if deltaTime.seconds >=5:
        
        print("OBJECT START")
        mainBox.setState()
        print("OBJECT END")
        print("Test lamp ... ")
        input_state = GPIO.input(25)           
        if input_state == False:
##          lastTimeLampOn = datetime.now()
          print colored('LAMP IS ON', 'green')
          time.sleep(7)
          ## It's Ok !
          ##
        else:
          print colored('LAMP IS OFF', 'red')
          time.sleep(2)
          lNow = datetime.now()
          deltaTime = lNow - lastTimeLampOn
          print (deltaTime)
          duration_in_s = deltaTime.total_seconds()
          minutes = divmod(duration_in_s, 60)[0] 
          print (minutes)
          if minutes>=lampCooling:
            GPIO.output(19, False)
            time.sleep(1)
            GPIO.output(19, True)
            time.sleep(2)
          input_state = GPIO.input(25)
          if input_state == False:
            print colored("____TRY TURN ON HID LAMP____","green")
            lampStat = 1
            if timesOfDay <> 1 :
              mylcd.lcd_load_custom_chars(fontdata1)
              mylcd.lcd_write(0x8D)
              mylcd.lcd_write_char(0)
              mylcd.lcd_write_char(1)
              mylcd.lcd_write_char(2)    
              mylcd.lcd_write(0xCD)
              mylcd.lcd_write_char(3)
              mylcd.lcd_write_char(4)
              mylcd.lcd_write_char(5)
              timesOfDay = 1
            lastTimeLampOn = datetime.now()
          else:
            timesOfDay = 0
            lampStat = 0
            
          time.sleep(7)  
        lNow = datetime.now()            
    else:
      ## NIGHT

      now = datetime.now()
      LampOff = now - lastTurnOff
      deltaTime = now - lNow      
      cls()
      print("NIGHT " + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "    delta "+ str( 30- deltaTime.seconds))
      input_state = GPIO.input(25)
      if input_state == False:
        print colored('LAMP IS ON', 'red')
      else:
        print colored('LAMP IS OFF', 'green')
##      deltaTime = lNow - lastTimeLampOn
      print ("   "+str(LampOff))
      duration_in_s = deltaTime.total_seconds()
      minutes = divmod(duration_in_s, 60)[0] 
      print ("  LAMP IS OFF " + str(minutes) + "minutes")

      if deltaTime.seconds >=10:
        print("Test lamp ... ")
        print("OBJECT START")
##        mainBox.setNeedState()
##        mainBox.setState()
##        mainBox.printx()
        mainBox.getInfo()
        #mainBox.setTermHumHome()
        mainBox.openComPort(0)
##        mainBox.setTermHumHome()
        #print (mainBox.lastState)
        print("OBJECT END")
        input_state = GPIO.input(25)
        if input_state == False:
          lastTimeLampOn = datetime.now()
          print colored('LAMP IS ON', 'yellow')
          print colored("____TRY TURN OFF HID LAMP____","yellow")        
          GPIO.output(19, True) 
          time.sleep(1)
          GPIO.output(26, False)
          time.sleep(1)
          GPIO.output(26, True)
          time.sleep(1)
          GPIO.output(19, True)
          time.sleep(1)
          input_state = GPIO.input(25)
          if input_state == True:
            lastTurnOff =  datetime.now()
            print colored('LAMP IS SHUTDOWN', 'green')
            mylcd.lcd_load_custom_chars(fontdata2)
            mylcd.lcd_write(0x8D)
            mylcd.lcd_write_char(0)
            mylcd.lcd_write_char(1)
            mylcd.lcd_write_char(2)    
            mylcd.lcd_write(0xCD)
            mylcd.lcd_write_char(3)
            mylcd.lcd_write_char(4)
            mylcd.lcd_write_char(5)             
            time.sleep(7)            
          else:
            print colored('ALARM!!! LAMP IS NOT POWER OFF', 'red')
            time.sleep(20)            
            #####################################################
            ##    TELEGRAM BOT !!!
            #####################################################
          lNow = datetime.now()
##          deltaTime = lNow - lastTimeLampOn
          ##
        else:
          print colored('LAMP IS OFF', 'green')
          #time.sleep(30)
          lNow = datetime.now()
##          deltaTime = lNow - lastTimeLampOn
          print ("   "+str(deltaTime))
          duration_in_s = deltaTime.total_seconds()
          minutes = divmod(duration_in_s, 60)[0] 
          print ("  LAMP IS OFF " + str(minutes) + "minutes")
          time.sleep(5)

##      now = datetime.now()
##      LampOff = now - lastTurnOff
##      deltaTime = now - lNow      

    #NIGHT


##    mylcd.lcd_load_custom_chars(fontdata1)
##    mylcd.lcd_write(0x8D)
##    mylcd.lcd_write_char(0)
##    mylcd.lcd_write_char(1)
##    mylcd.lcd_write_char(2)    
##    mylcd.lcd_write(0xCD)
##    mylcd.lcd_write_char(3)
##    mylcd.lcd_write_char(4)
##    mylcd.lcd_write_char(5)
##    time.sleep(2)
##    mylcd.lcd_write(0x8D)
##    mylcd.lcd_write_char(6)
##    mylcd.lcd_write_char(7)
##    mylcd.lcd_write_char(8)
    time.sleep(1)
    # test 2
    #mylcd.lcd_display_string("RPi I2C test", 1)
    #mylcd.lcd_display_string(" Custom chars", 2)

    #sleep(2) # 2 sec delay


    #lcd_string(datetime.now().strftime("%Y/%m/%d"),  LCD_LINE_1)
    #lcd_string(datetime.now().strftime("%H:%M:%S"),  LCD_LINE_2)

if __name__ == '__main__':
  timeOn = now.replace(hour=8, minute=00, second=0, microsecond=0)
  timeOff = now.replace(hour=22, minute=00, second=0, microsecond=0)

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    pass
    #lcd_byte(0x01, LCD_CMD)






 
