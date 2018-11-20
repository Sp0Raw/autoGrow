#! /usr/bin/env python
# coding: utf-8
 
import serial
 
ser = serial.Serial("/dev/ttyACM0")
ser.baudrate = 9600
 
while True :
  line = ser.readline()
  print line
  ser.close()
