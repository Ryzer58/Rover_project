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
from time import perf_counter_ns
import serial
from serial.tools import list_ports
from flask import Flask, render_template, request

app = Flask (__name__, template_folder='web-app/', static_folder='web-app/static/')

# Rover operating parameters to be populated by information collected from Arduino like that used in the intial
# cli based program

min_throttle = 0
max_throttle = 0
num_mot = 0
throttle = 0
throttle_level = 100
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

timer_enabled = True
timer_start = 0
timer_duration = 0 #Just a place holder for a counter yet to be implemented
func = 0


# Serial Port detection and configuration - First look for available devices (Still need to add proper error handling system)

myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
print (myports)

arduLink = '/dev/ttyS1'

for port in myports:
    if '/dev/ttyACM0' in port:
        arduLink = '/dev/ttyACM0'
        print("ACM device found - Most likely Arduino UNO")
    elif '/dev/ttyUSB0' in port:
        arduLink = '/dev/ttyUSB0'
        print("USB device found - Most likely Nano/clone")
        
piComm = serial.Serial(arduLink,19200,timeout = 2)
piComm.flush()
rover_param = piComm.readline().decode('utf-8')
rover_param = rover_param.split("; ")
motor_range, servo_range = rover_param

motData= motor_range.lstrip('Motor: ') # The first string sent will contain the motor data as defined in the Arduino setup function
motData = motData.split(",")
print("Motor Configuration: ")
for m in range(len(motData)):
    motParam[m] = int(motData[m])
    print(motLabel[m] + str(motData[m])) #Print back the retrieved value

servoData = servo_range.lstrip('Servo: ') # The second string will contain the Servo constraints
servoData = servoData.split(",")
print("Servo configuaration: ")
for s in range(len(servoData)):
    servoParam[s] = int(servoData[s])
    print(servoLabel[s] + str(servoData[s]))
    
min_throttle, max_throttle, num_mot = [motParam[i] for i in [0 , 1, 2]]
serCentre, serLeft, serRight = [servoParam[n] for n in [0, 1, 2]]


# Data processing functions

def transmit(function, param0, param1):
    
    PiCommand = [str(function),str(param0),str(param1)]
    outGoing = (','.join(PiCommand) + '\n')
    piComm.write(outGoing.encode('utf-8'))

def recieve():
    incoming = piComm.readline().decode('utf-8').rstrip()
    recievedData = incoming.split(",")

    return recievedData

# TODO - once we have got the control data to render correctly on the page with the
# data automatically refreshing we can then worry about handling the return data


def move_forward():
   global throttle, throttle_level, direction

   if direction != True and throttle > min_throttle:

      stop()
      
      direction = True

   throttle = throttle_level

   return direction, throttle

def move_reverse():
   global throttle, direction

   if direction != False and throttle > min_throttle:

      stop()

      direction = False

   throttle = throttle_level

   return direction, throttle

        
def bear_left():  
   global str_pos, serLeft

   if str_pos > serLeft:
      
      str_pos -= 5
   
   return str_pos
           
def sw_right():
   global str_pos, serRight

   if str_pos < serRight:

      str_pos += 5

   return str_pos


def reset():
    transmit('0','0','30')

def stop():
    transmit('0','0',str(str_pos))


# Core movement controls 

@app.route("/")
def index():
   return render_template("index.html", name = None, direction=direction, acceleration=throttle)

@app.route("/forward")
def forward():
   global num_mot, timer_enabled, timer_start

   print("Forward")

   direction, power = move_forward()

   if timer_enabled == True:

      timer_start = perf_counter_ns()
      
   return render_template("index.html", direction=direction, acceleration=power)

@app.route("/backward")
def reverse():
   global num_mot, timer_enabled, timer_start

   print("Backward")

   direction, power = move_reverse()
   
   if timer_enabled == True:

      timer_start = perf_counter_ns()

   return render_template('index.html', direction=direction, acceleration=power)

@app.route("/left")
def left():
   global num_mot

   print("Left")
   steer_pos = bear_left()
   
   return render_template('index.html', steering=steer_pos)

@app.route("/right")
def right():
   global num_mot

   print("Right")
   steer_pos = sw_right()

   return render_template('index.html', steering=steer_pos)

@app.route("/stop")
def em_stop():
   global throttle

   stop()

   print("Stopped")
   
   return render_template('index.html', acceleration=throttle)


# Throttle/PWM level, Currently configured as 3 preset values with a later goal being to implement a slide bar 
# for more fine grained control.

@app.route("/speed_low")
def speed_low():
   global throttle_level

   throttle_level = 100

   return render_template("index.html")
   

@app.route("/speed_mid")
def speed_mid():
   global throttle_level

   throttle_level = 170 
   
   return render_template("index.html")


@app.route("/speed_hi")
def speed_hi():
   global throttle_level

   throttle_level = 245
      
   return render_template("index.html")

# Run time - a counter for controlling the duration for which the rover moves, again the implements a set of predefined speeds that range from 'short' to
# continous where the counter is disabled and the motors will keep on running unless a stop command is sent 

@app.route("/continuous") #running duration
def continuous():
   global timer_duration, timer_enabled

   print("Continuous run")
   timer_enabled = False
   timer_duration = 0
   
   return render_template('index.html')

@app.route("/mid_run")
def mid_run():
   global timer_duration, timer_enabled

   print("Mid run")
   timer_duration = 5000000000
   timer_enabled = True

   return render_template('index.html')

@app.route("/short_time")
def short_time():
   global timer_duration, timer_enabled

   print("Short run")
   timer_duration = 2000000000
   timer_enabled = True
   
   return render_template('index.html')

# Camera panning controls (Not yet implemented on Arduino side):

@app.route("/panlt")
def panlf( ):
   global pan_pos

   print("Panlt")
   pan_pos += 5
   if pan_pos < 135:
      pan_pos = 135
   
   return render_template("index.html", bearing=pan_pos)

@app.route("/panrt")
def panrt():
   global pan_pos

   print("Panrt")
   pan_pos -= 5
   if pan_pos > 45:
      pan_pos = 45
  
   return render_template("index.html", bearing=pan_pos)

@app.route ("/home")
def home():
   global pan_pos

   print("Home")
  
   return render_template("index.html", bearing=pan_pos)

@app.route("/panfull_lt")
def panfull_lt():
   global pan_pos

   print("Pan full left")
   
   return render_template("index.html", bearing=pan_pos)

@app.route("/panfull_rt")
def panfull_rt():
   global pan_pos

   print ("Pan full right")
   
   return render_template("index.html", bearing=pan_pos)


# This needs to be sent periodically in a way that does not block the rest of the script. One
# way to achieve this could be using the systems primary counter (perf) to compare time elapsed
# in a similiar way to millis on the arduino

transmit(func, throttle, str_pos)

if timer_enabled == True: # If not continuous, then  stop after delay

      timer_current = perf_counter_ns()

      if timer_current - timer_start > timer_duration:

         stop()

         timer_enabled = False

      
#recieve() - need to add once I find a way to forward the measurements onto the webpage

if __name__ == "__main__" :
   app.run (host = 'localhost', port = 5000, debug = False)
   
   # disable debug due to cause reset which cause intial setup to rerun which of course
   # will lead to it failing on the second run as the arduino will only issue this data once.
   # Replace local host with either the IP address or the Hostname of the SBC.
