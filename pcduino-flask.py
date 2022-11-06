#!/usr/bin/env python
#
# Wifi/Web driven Rover
#
# Written by Ryzer - 2021
#
# Uses Adafruit Blinka, pyserial and Flask
#
# A Pcduino running an Armbian based image.
# Ensure that the overlays for both I2C2
# AND PWM overlay are enabled prior to using.
# The Pcduino has 2 hardware capble PWM which
# can be selected below

import time
import sys
import serial
import board #Import the board profile from Blinka libraries
import digitalio
from adafruit_servokit import ServoKit #I2C servo shield libraries
from pcduino import pwmSet
from flask import Flask, render_template, request

app = Flask (__name__, static_url_path = '')

try:
   # Change the baud rate here if diffrent than 19200
   gps_nav = serial.Serial ('/dev/ttyS2', 9600)
except IOError:
   print ("GPS not found")
   sys.exit (0)

#Motor 1 configuration - connect matching jumper on dir A header
dir_1 = digitalio.DigitalInOut(board.D2)
#dir_1 = digitalio.DigitalInOut(board.D4)
#dir_1 = digitalio.DigitalInOut(board.D7)
dir_1.direction = digitalio.Direction.OUTPUT

Throttle_1 = "pwm0" #Pin 5 Pcduino

#Motor 2 configuration - connect matching jumper on dir B header
#dir_2 = digitalio.DigitalInOut(board.D8)
#dir_2 = digitalio.DigitalInOut(board.D12)
#dir_2 = digitalio.DigitalInOut(board.D13)
#dir_2.direction = digitalio.Direction.OUTPUT

#Throttle_2 = "pwm1" #Pin 6 Pcduino

# Speed and drive control variables - remember to set pwm and directional control variables
pwmSet.pulseDuration(Throttle_1, 1000000)
pwmSet.pulseDuty(Throttle_1, 0) #start at a stationary position
pwmSet.polarity(Throttle_1, 0)
pwmSet.enable(Throttle_1, 1)
speed_offset = 84
run_time = 0.750



# Servo neutral position (home)
kit = ServoKit(channels=16)
kit.servo[0].angle = 90 #Steering servo
#kit.servo[1].angle = 90 #Camera pan servo
turn_offset = 0.166

pan_serv
#dri_serv #Reserved for later use when implementing a camera pivot

time.sleep (3) # A little dwell for settling down time

#
# URI handlers - all the bot page actions are done here
#
# Send out the bots control page (home page)

@app.route ("/")
def index ( ):
   return render_template ('index.html', name = None)

@app.route ("/forward")
def forward ( ):
   global run_time

   print ("Forward")
   dir_1.value = True
   go_forward ( )
   
   time.sleep (0.100 + run_time) # sleep 100ms + run_time

   if run_time > 0:  # If not continuous, then halt after delay
      halt ( )

   return "ok"

@app.route ("/backward")
def backward ( ):
   global run_time

   print ("Backward")
   dir_1.value = False
   go_backward()
   
   time.sleep (0.100 + run_time) # sleep 100ms + run_time
   
   if run_time > 0: # If not continuous, then halt after delay
      halt ( )

   return "ok"

@app.route ("/left")
def left ( ):
   global turn_offset

   print ("Left")
   sw_left()
   
   time.sleep (0.500 - turn_offset) # sleep @1/2 second
   
   halt ( ) # stop
   time.sleep (0.100)
   return "ok"

@app.route ("/right")
def right ( ):
   global turn_offset

   print ("Right")
   sw_right ( )

   time.sleep (0.500 - turn_offset) # sleep @1/2 second - need to adjust for servp

   halt ( ) # stop
   time.sleep (0.100)
   return "ok"

@app.route ("/sharpLfFor")
def sharpLfFor ( ):
   global turn_offset

   print ("Left forward turn")
   dir_1.value = True
   sw_left ( )
   go_forward

   time.sleep (0.250 - (turn_offset / 2)) # sleep @1/8 second
   
   halt ( ) # stop
   time.sleep (0.100)
   return "ok"

@app.route ("/sharpLfRev")
def sharpLfRev ( ):
   global turn_offset

   print ("Left forward turn")
   dir_1.value = False
   sw_left( )
   go_backward()

   time.sleep (0.250 - (turn_offset / 2)) # sleep @1/8 second
   
   halt ( ) # stop
   time.sleep (0.100)
   return "ok"
   
@app.route ("/sharpRtFor")
def sharpRtFor ( ):
   global turn_offset

   print ("Right forward turn")
   dir_1.value = True
   sw_right ( )
   go_forward()
   
   time.sleep (0.250 - (turn_offset / 2)) # sleep @1/8 second

   halt ( ) # stop
   time.sleep (0.100)
   return "ok"
   
@app.route ("/sharpRtRev")
def sharpRtRev ( ):
   global turn_tm_offset

   print ("Right forward turn")
   dir_1.value = False
   sw_right ( )
   go_backward()

   time.sleep (0.250 - (turn_offset / 2)) # sleep @1/8 second

   halt ( ) # stop
   time.sleep (0.100)
   return "ok"

@app.route ("/stop")
def stop ( ):
   global last_direction

   print ("Stop")
   halt ( )

   time.sleep (0.100) # sleep 100ms
   return "ok"


@app.route ("/panlt") #Cam Servo control functions
def panlf ( ):
   global pan_serv

   print ("Panlt")
   pan_serv += 5
   if pan_serv < 135:
      pan_serv = 135
   kit.servo[0].angle = pan_serv
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/panrt")
def panrt ( ):
   global pan_serv

   print ("Panrt")
   pan_serv -= 5
   if pan_serv > 45:
      pan_serv = 45
   kit.servo[0].angle = pan_serv
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/home")
def home ( ):
   global pan_serv

   print ("Home")
   kit.servo[0].angle = 90
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/panfull_lt")
def panfull_lt ( ):
   global pan_serv

   print ("Pan full left")
   kit.servo[1].angle = 135
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/panfull_rt")
def panfull_rt ( ):
   global pan_serv

   print ("Pan full right")
   kit.servo[1].angle = 45
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/speed_low")
def speed_low ( ):
   global speed, turn_offset

   speed = 42 #Calibrate according to motor used 
   turn_offset = 0.001
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/speed_mid") #speed control presets
def speed_mid ( ):
   global speed, turn_offset

   speed = 84
   turn_tm_offset = 0.166   
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/speed_hi")
def speed_hi ( ):
   global speed, last_direction, turn_offset

   speed = 126
   turn_offset = 0.332
   time.sleep (0.150) # sleep 150ms
   return "ok"

@app.route ("/continuous") #running duration
def continuous ( ):
   global run_time

   print ("Continuous run")
   run_time = 0
   time.sleep (0.100) # sleep 100ms
   return "ok"

@app.route ("/mid_run")
def mid_run ( ):
   global run_time

   print ("Mid run")
   run_time = 0.750
   halt ( )
   time.sleep (0.100) # sleep 100ms
   return "ok"

@app.route ("/short_time")
def short_time ( ):
   global run_time

   print ("Short run")
   run_time = 0.300
   halt ( )
   time.sleep (0.100) # sleep 100ms
   return "ok"

def go_forward ( ): # Motor drive functions
    global speed
    
    dir_1.value = True
    pwmSet.pulseDuty(Throttle_1, speed)
        
def go_backward ( ):
    global speed

    dir_1.value = False
    pwmSet.pulseDuty(Throttle_1, speed)
        
   

def sw_left ( ): # Servo steering functions
    global dri_serv

    dri_serv += 5
    if dri_servo > 105:
        dri_servo = 105
    kit.servo[0].angle = dri_serv
        
def sw_right ( ):
    global dri_serv

    dri_serv -= 5
    if dri_servo < 65:
        dri_servo = 65
    kit.servo[0].angle = dri_serv

def halt ( ):
    pwmSet.pulseDuty(Throttle_1, 0)
    kit.servo[0].angle = 90

if __name__ == "__main__" :
   app.run (host = '0.0.0.0', port = 80, debug = True)
