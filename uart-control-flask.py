#!/usr/bin/env python
#
# Wifi/Web driven Rover -- Hybrid version
#
# Written by Ryzer - 2021/2022 (v1.0)
#
# Uses Adafruit Blinka, pyserial and Flask
#
# A Pcduino running an Armbian based image.
# Ensure that the overlays for both I2C2
# AND PWM overlay are enabled prior to using.
# The Pcduino has 2 hardware capble PWM which
# can be selected below

import sys
import time
import serial
from flask import Flask, render_template, request

app = Flask (__name__, static_url_path = '')

#TODO - Modify the intial Pcduino flask script to instead send comands over serial
#Remove useless control statements

#like with the cli test begin by intialising serial communication

#Predefine controller information to be adjusted based on data fetched back from the Arduino

forMin = 0
forMax = 0
revMin = 0
revMax = 0

motParam = [revMin, revMax, forMin, forMax]
motLabel = ['Min Reverse ', 'Max Reverse ','Min Forward ','Max Forward ']

serRight = 0
serCentre = 0
serLeft = 0

servoParam = [serCentre, serLeft, serRight]
servoLabel = ['Centre ','Max left ','Max right ']

pos = 30
speed = 0
run_time = 0 #Just a place holder for a counter yet to be implemented
arc_time = 1945 #todo time for the servo to swing 60 degree in microseconds (more use for automation rather than in manual mode)
func = 0

speedLock = 0

myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
print (myports)

#Configure active serial port
for port in myports:
    if '/dev/ttyACM0' in port:
        arduLink = '/dev/ttyACM0'
        print("ACM device found - Most likely Arduino UNO")
    elif '/dev/ttyUSB0' in port:
        arduLink = '/dev/ttyUSB0'
        print("USB device found - Most likely Nano/clone")

        
piComm = serial.Serial(arduLink,19200,timeout = 2)
piComm.flush()

# Admittedly this is probably not the most efficient way of doing things, I will look for a better way
# in the future but for now it should work for simply retrieving motor parameters from the Arduino
motor = piComm.readline().decode('utf-8').lstrip('Motor: ') # Firstly read back motor configuration from Arduino
motData = motor.split(",")
print("Motor Configuration: ")
for m in range(len(motData)):
    motParam[m] = int(motData[m])
    print(motLabel[m] + str(motData[m])) #Print back the retrieved value

servo = piComm.readline().decode('utf-8').lstrip('Servo: ') # Second read back servo parameters from Arduino
servoData = servo.split(",")
print("Servo configuaration: ")
for s in range(len(servoData)):
    servoParam[s] = int(servoData[s])
    print(servoLabel[s] + str(servoData[s]))
    
#ensure values are actually set, doesnt quite work the same way as arduino, not the best way to do #things but should work

revMin, revMax, forMin, forMax = [motParam[i] for i in [0 , 1, 2, 3]]
serCentre, serLeft, serRight = [servoParam[n] for n in [0, 1, 2]]

#
# URI handlers - all the bot page actions are done here
#
#



# Data processing functions

def transmit():
    toSend = (','.join(PiCommand) + '\n')
    piComm.write(toSend.encode('utf-8'))

def recieve():
    toRecieve = piComm.readline().decode('utf-8').rstrip()
    recieveData = toRecieve.split(",")



def go_forward(): # Motor drive functions
    global speed

    if speed == 0 or speed < forMin:

      speed = speed + 180
      #need to add a better means to deal with different speed profiles

def go_backward():
    global speed

    if speed == 0 or speed > revMax:

      speed = speed - 180

        
def sw_left(): # Servo steering functions
    global dri_servo

    if dri_servo > serLeft:
      dri_servo -= 5
   
    #place serial command for turning left
        
def sw_right():
    global dri_serv

    if dri_servo < serRight:

      dri_serv += 5

    #place serial command for turning right

def reset():
    reset = ['0','30','0']
    transmit()

def stop():
    stopping = ['0',str(pos),'0',]
    transmit()


# Core movement controls 

@app.route("/")
def index( ):
   return render_template('index.html', name = None)

@app.route("/forward")
def forward( ):
   global run_time

   print("Forward")

   go_forward()

   if run_time > 0:  # If not continuous, then  stop after delay

      time.sleep(0.100 + run_time) # sleep 100ms + run_time

      stop()

   return "ok"

@app.route("/backward")
def backward( ):
   global run_time

   print("Backward")

   go_backward()
   
   if run_time > 0: # If not continuous, then   stop after delay

      time.sleep(0.100 + run_time) # sleep 100ms + run_time

      stop()

   return "ok"

@app.route("/left")
def left():
   global turn_offset

   print("Left")
   sw_left()
   
   time.sleep(0.500 - turn_offset) # sleep @1/2 second
   
   stop()
   time.sleep(0.100)
   return "ok"

@app.route("/right")
def right():
   global turn_offset

   print("Right")
   sw_right()

   time.sleep(0.500 - turn_offset) # sleep @1/2 second - need to adjust for servp

   stop() # stop
   time.sleep(0.100)
   return "ok"

@app.route("/stop")
def stop():
   global last_direction

   print("Stopping")
   stop()

   time.sleep(0.100) # sleep 100ms
   return "ok"

# Speed profiles, 3 preset speeds with a later goal being to implement a slide bar control to increase flexibility
# over the over

@app.route("/speed_low")
def speed_low():
   global speed, turn_offset

   speed = 100
   turn_offset = 0.001
   time.sleep(0.150)
   return "ok"

@app.route("/speed_mid")
def speed_mid():
   global speed, turn_offset

   speed = 170
   turn_tm_offset = 0.166   
   time.sleep(0.150)
   return "ok"

@app.route("/speed_hi")
def speed_hi():
   global speed, last_direction, turn_offset

   speed = 245
   turn_offset = 0.332
   time.sleep(0.150)
   return "ok"

# Run time - a counter for controlling the duration for which the rover moves, again the implements a set of predefined speeds that range from 'short' to
# continous where the couter is disabled and the motors will keep on running unless a stop command is sent 

@app.route("/continuous") #running duration
def continuous():
   global run_time

   print("Continuous run")
   run_time = 0
   time.sleep(0.100) # sleep 100ms
   return "ok"

@app.route("/mid_run")
def mid_run():
   global run_time

   print("Mid run")
   run_time = 0.750
   stop()
   time.sleep(0.100) # sleep 100ms
   return "ok"

@app.route("/short_time")
def short_time():
   global run_time

   print("Short run")
   run_time = 0.300
   stop()
   time.sleep (0.100) # sleep 100ms
   return "ok"



# All Camera related controls (dummy not yet implemented):

@app.route("/panlt") #Cam Servo control functions
def panlf( ):
   global pan_serv

   print("Panlt")
   pan_serv += 5
   if pan_serv < 135:
      pan_serv = 135

   time.sleep(0.150) # sleep 150ms
   return "ok"

@app.route("/panrt")
def panrt():
   global pan_serv

   print("Panrt")
   pan_serv -= 5
   if pan_serv > 45:
      pan_serv = 45

   time.sleep(0.150) # sleep 150ms
   return "ok"

@app.route ("/home")
def home():
   global pan_serv

   print("Home")

   time.sleep(0.150) # sleep 150ms
   return "ok"

@app.route("/panfull_lt")
def panfull_lt():
   global pan_serv

   print("Pan full left")

   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route("/panfull_rt")
def panfull_rt():
   global pan_serv

   print ("Pan full right")

   time.sleep(0.150) # sleep 150ms
   return "ok"


PiCommand = [str(speed),str(pos),str(func)] #functions are work in progress so stub for now
transmit()
#recieve() - need to add once I find a way to forward the measurements onto the webpage

if __name__ == "__main__" :
   app.run (host = '0.0.0.0', port = 80, debug = True)
