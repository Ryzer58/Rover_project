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

time_limit = True
run_time = 0 #Just a place holder for a counter yet to be implemented
#arc_time = 1945 #todo time for the servo to swing 60 degree in microseconds (more use for automation rather than in manual mode)
func = 0

speedLock = 0


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

def transmit(data1, data2, data3):
    
    PiCommand = [str(data1),str(data2),str(data3)]
    outGoing = (','.join(PiCommand) + '\n')
    piComm.write(outGoing.encode('utf-8'))

def recieve():
    incoming = piComm.readline().decode('utf-8').rstrip()
    recievedData = incoming.split(",")

    return recievedData

    #Once the dash board is working we can move onto processing incoming data


def move_forward():
   global throttle_level, direction

   if direction != True and throttle > min_throttle:

      stop()
      
      direction = True

   throttle = throttle_level

   return direction, throttle

def move_reverse():
   global throttle_level, direction, profile

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

def run_timer(interval):

   time.sleep(interval)


# Core movement controls 

@app.route("/")
def index( ):
   return render_template("index.html", name = None)

@app.route("/forward")
def forward():
   global num_mot, run_time, func, time_limit

   print("Forward")

   direction, power = move_forward()

   # Need a better alternative to sleep which freezes controls

   # Ideally if we implemented some kind of time it would allow us to steer while moving

   if time_limit == True:  # If not continuous, then  stop after delay

      time.sleep(0.100 + run_time) # sleep 100ms + run_time

      stop()

      direction = str(direction)

      power = str(power)

   return render_template('index.html', direction=direction, acceleration=power)

@app.route("/backward")
def reverse():
   global num_mot, run_time, func, time_limit

   print("Backward")

   direction, power = move_reverse()
   
   if time_limit == True: # If not continuous, then   stop after delay

      time.sleep(0.100 + run_time) # sleep 100ms + run_time

      stop()

   direction = str(direction)

   power = str(power)

   return render_template('index.html', acceleration=direction, acceleration=power)

@app.route("/left")
def left():
   global num_mot

   print("Left")
   steer_pos = bear_left()
   
   # Keep it simple for now but we may later decide to include an offset for the time it takes the servo to get into position
   time.sleep(0.05) # sleep @1/2 second

   steer_pos = str(steer_pos)
   
   return render_template('index.html', steering=steer_pos)

@app.route("/right")
def right():
   global num_mot

   print("Right")
   steer_pos = sw_right()

   time.sleep(0.05) # sleep @1/2 second - need to adjust for servo

   steer_pos = str(steer_pos)

   return render_template('index.html', steering=steer_pos)

@app.route("/stop")
def em_stop():
   global throttle

   stop()

   time.sleep(0.1) # sleep 100ms

   print("Stopped")

   throttle = str(throttle)
   
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
   global run_time, time_limit

   print("Continuous run")
   time_limit = False
   
   return render_template('index.html')

@app.route("/mid_run")
def mid_run():
   global run_time, time_limit

   print("Mid run")
   run_time = 0.750
   time_limit = True

   return render_template('index.html')

@app.route("/short_time")
def short_time():
   global run_time, time_limit

   print("Short run")
   run_time = 0.300
   time_limit = True
   
   return render_template('index.html')

# All Camera related controls (Yet to be implemented):

@app.route("/panlt") #Cam Servo control functions
def panlf( ):
   global pan_pos

   print("Panlt")
   pan_pos += 5
   if pan_pos < 135:
      pan_pos = 135

   time.sleep(0.150) # sleep 150ms
   
   return render_template("index.html", bearing=str(pan_pos))

@app.route("/panrt")
def panrt():
   global pan_pos

   print("Panrt")
   pan_pos -= 5
   if pan_pos > 45:
      pan_pos = 45

   time.sleep(0.150) # sleep 150ms
   
   return render_template("index.html", bearing=str(pan_pos))

@app.route ("/home")
def home():
   global pan_pos

   print("Home")

   time.sleep(0.150) # sleep 150ms
  
   return render_template("index.html", bearing=str(pan_pos))

@app.route("/panfull_lt")
def panfull_lt():
   global pan_pos

   print("Pan full left")

   time.sleep (0.150) # sleep 150ms
   
   return render_template("index.html", bearing=str(pan_pos))

@app.route("/panfull_rt")
def panfull_rt():
   global pan_pos

   print ("Pan full right")

   time.sleep(0.150) # sleep 150ms
   
   return render_template("index.html", bearing=str(pan_pos))


# This needs to be sent periodically in a way that does not block the rest of the script

transmit(func, throttle, str_pos)

#check_timer()

#recieve() - need to add once I find a way to forward the measurements onto the webpage

if __name__ == "__main__" :
   app.run (host = '192.168.0.242', port = 5000, debug = False)
   # disable debug due to cause reset which cause intial setup to rerun which of course
   # will lead to it failing on the second run as the arduino will only issue this data once.
