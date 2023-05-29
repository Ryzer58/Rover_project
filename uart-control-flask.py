#!/usr/bin/env python
#
# Wifi/Web driven Rover -- Hybrid version
#
# Written by Ryzer - 2021/2022 (v1.0)
#
# Uses pyserial and Flask
# Adafruit Blinka may be used if going down the approuch of incorprating less time dependant functions
#
# Main control script, for connecting to the microcontroller handling the time sensitive operations of
# controlling motors and reading sensors. If using RaspberryPi with Raspian OS we will most likely be
# using USB ports so not much software configuration will be needed. If using the Pcduino or any
# SBC that is running Armbian be sure to activate the appropriate Serial Overlay. 
# 

import sys
import time
import serial
from flask import Flask, render_template, request

app = Flask (__name__, static_url_path = '')

# Rover operating parameters to be populated by information collected from Arduino like that used in the intial
# cli based program

min_throttle = 0
max_throttle = 0
num_mot = 0
throttle = 0
profile = throttle
direction = True

motParam = [min_throttle, max_throttle, num_mot,]
motLabel = ['Min throttle ', 'Max throttle ', 'Motors ']

serRight = 0
serCentre = 0
serLeft = 0
str_pos = 30
pan_pos = 90

servoParam = [serCentre, serLeft, serRight]
servoLabel = ['Centre ','Max left ','Max right ']



run_time = 0 #Just a place holder for a counter yet to be implemented
arc_time = 1945 #todo time for the servo to swing 60 degree in microseconds (more use for automation rather than in manual mode)
func = 0

speedLock = 0

# Serial Port detection and configuration

myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
print (myports)

arduLink = '/dev/ttyS1'

for port in myports:
    if '/dev/ttyACM0' in port:
        arduLink = '/dev/ttyACM0'
        print("ACM device found - Most likely Arduino UNO") # Could also be any other AVR device
    elif '/dev/ttyUSB0' in port:
        arduLink = '/dev/ttyUSB0'
        print("USB device found - Most likely Nano/clone")
        
piComm = serial.Serial(arduLink,19200,timeout = 2)
piComm.flush()

motor = piComm.readline().decode('utf-8').lstrip('Motor: ') # The first string sent will contain the motor data as defined in the Arduino setup function
motData = motor.split(",")
print("Motor Configuration: ")
for m in range(len(motData)):
    motParam[m] = int(motData[m])
    print(motLabel[m] + str(motData[m])) #Print back the retrieved value

servo = piComm.readline().decode('utf-8').lstrip('Servo: ') # The second string will contain the Servo constraints
servoData = servo.split(",")
print("Servo configuaration: ")
for s in range(len(servoData)):
    servoParam[s] = int(servoData[s])
    print(servoLabel[s] + str(servoData[s]))
    
min_throttle, max_throttle, num_mot = [motParam[i] for i in [0 , 1, 2]]
serCentre, serLeft, serRight = [servoParam[n] for n in [0, 1, 2]]


# Data processing functions

def transmit(data1, data2, data3):
    
    PiCommand = [str(data1),str(data2),str(data3),]
    outGoing = (','.join(PiCommand) + '\n')
    piComm.write(outGoing.encode('utf-8'))

def recieve():
    incoming = piComm.readline().decode('utf-8').rstrip()
    recievedData = incoming.split(",")

    return recievedData

    #Once the dash board is working we can move onto processing incoming data


def go_forward():
   global throttle, direction, profile

   if throttle == 0 or throttle < min_throttle:

      throttle = 170

   if direction != True and throttle > min_throttle:

      stop()
      
      direction = True

      throttle = profile

   return direction

def go_reverse():
   global throttle, direction, profile

   if throttle == 0 or throttle < min_throttle:

      throttle = 170

   if direction != False and throttle > min_throttle:

      stop()

      direction = False

      throttle = profile

   return direction

        
def sw_left(): 
    global str_pos

    if str_pos > serLeft:
      str_pos -= 5
   
    
        
def sw_right():
    global str_pos

    if str_pos < serRight:

      str_pos += 5

    #place serial command for turning right

def reset():
    reset = ['0','0','30']
    transmit()

def stop():
    stopping = ['0','0',str(str_pos),]
    transmit()

def run_timer(interval):

   time.sleep(interval)


# Core movement controls 

@app.route("/")
def index( ):
   return render_template('index.html', name = None)

@app.route("/forward")
def forward():
   global run_time, func

   print("Forward")

   func=go_forward()

   # Need a better alternative to sleep which freezes controls

   # Ideally if we implemented some kind of time it would allow us to steer while moving

   if time_limit == True:  # If not continuous, then  stop after delay

      time.sleep(0.100 + run_time) # sleep 100ms + run_time

      stop()

   return "ok"

@app.route("/backward")
def reverse():
   global run_time, func

   print("Backward")

   func=go_reverse()
   
   if time_limit == True: # If not continuous, then   stop after delay

      time.sleep(0.100 + run_time) # sleep 100ms + run_time

      stop()

   return "ok"

@app.route("/left")
def left():
   global turn_offset

   print("Left")
   sw_left()
   
   # Keep it simple for now but we may later decide to include an offset for the time it takes the servo to get into position
   time.sleep(0.05) # sleep @1/2 second
   
   return "ok"

@app.route("/right")
def right():
   global turn_offset

   print("Right")
   sw_right()

   time.sleep(0.05) # sleep @1/2 second - need to adjust for servo

   return "ok"

@app.route("/stop")
def stop():

   print("Stopping")
   stop()

   time.sleep(0.1) # sleep 100ms
   return "ok"

# Throttle/PWM level, Currently configured as 3 preset values with a later goal being to implement a slide bar 
# for more fine grained control.

@app.route("/speed_low")
def speed_low():
   global throttle, turn_offset, profile

   throttle = 100
   profile = throttle
   turn_offset = 0.001
   time.sleep(0.150)
   return "ok"

@app.route("/speed_mid")
def speed_mid():
   global throttle, turn_offset, profile

   throttle = 170
   profile = throttle
   turn_offset = 0.166   
   return "ok"

@app.route("/speed_hi")
def speed_hi():
   global throttle, turn_offset, profile

   throttle = 245
   profile = throttle
   turn_offset = 0.332
   return "ok"

# Run time - a counter for controlling the duration for which the rover moves, again the implements a set of predefined speeds that range from 'short' to
# continous where the counter is disabled and the motors will keep on running unless a stop command is sent 

@app.route("/continuous") #running duration
def continuous():
   global run_time, time_limit

   print("Continuous run")
   time_limit = False
   
   return "ok"

@app.route("/mid_run")
def mid_run():
   global run_time, time_limit

   print("Mid run")
   run_time = 0.750
   time_limit = True

   return "ok"

@app.route("/short_time")
def short_time():
   global run_time, time_limit

   print("Short run")
   run_time = 0.300
   time_limit = True
   
   return "ok"

# All Camera related controls (Stub yet to be implemented):

@app.route("/panlt") #Cam Servo control functions
def panlf( ):
   global pan_pos

   print("Panlt")
   pan_pos += 5
   if pan_pos < 135:
      pan_pos = 135

   time.sleep(0.150) # sleep 150ms
   return "ok"

@app.route("/panrt")
def panrt():
   global pan_pos

   print("Panrt")
   pan_pos -= 5
   if pan_pos > 45:
      pan_pos = 45

   time.sleep(0.150) # sleep 150ms
   return "ok"

@app.route ("/home")
def home():
   global pan_pos

   print("Home")

   time.sleep(0.150) # sleep 150ms
   return "ok"

@app.route("/panfull_lt")
def panfull_lt():
   global pan_pos

   print("Pan full left")

   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route("/panfull_rt")
def panfull_rt():
   global pan_pos

   print ("Pan full right")

   time.sleep(0.150) # sleep 150ms
   return "ok"


# This needs to be sent periodically in a way that does not block the rest of the script

transmit(func, throttle, str_pos)

#check_timer()

#recieve() - need to add once I find a way to forward the measurements onto the webpage

if __name__ == "__main__" :
   app.run (host = '0.0.0.0', port = 80, debug = True)
