#!/usr/bin/env python
#
# Wifi/Web driven Rover -- Hybrid version
#
# Written by Ryzer - 2023 (v1.2)
#
# Rover control script using a companion microcontroller for more time senstive operations. The main Libraries used
# are Flask, pyserial and Adafruit Blinka for any onboard IO used where timing is no so greatly an issue.
# Adafruit Blinka may be used if going down the approuch of incorprating less time dependant functions. This has
# primarily been test on The Raspberry Pi 3 and The Pcduino 2 although with a few minor adjust it can work with
# other boards so long as they have the hardware requirements. Depending on what is avaliable, certian interfaces
# may need to be configured differently. In the case of Using the Raspberry Pi not much needs to be done other
# than checking the connections. For the Pcduino we need to make sure that the otg port is configure in host mode
# and than the Serial overlay is loaded on the Armbian OS.

# Currently have 4 supported functions

import sys
from time import perf_counter_ns, sleep
import serial
from serial.tools import list_ports
from flask import Flask, render_template, request

app = Flask (__name__, template_folder='web-app/', static_folder='web-app/static/')

# Rover operating parameters to be populated by information collected from Arduino like that used in the intial
# cli based program

throttle = 0
throttle_level = 100
direction = True
motRange = (70, 255) # Min, Max, Number of motors attached

str_pos = 30
pan_pos =  90 # not yet tested
servoRange = (30, 0, 60) # Centre, Left, Right
panRange = (45, 90, 135)

timer_enabled = True
timer_start = 0
timer_duration = 0
func = 0


# Serial Port detection mechanism:
# Scan attached serial devices looking for an Arduino or similar/microcontroller if found we then 
# assign it as our target for communication. This is a work in progress that will not to account 
# if connection is lost and regained. If this occurs it could cause the device number to jump in 
# which case this will fail.

myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
arduLink = ' '

for port in myports:
    if '/dev/ttyACM0' in port:
        arduLink = '/dev/ttyACM0'
        print("ACM device found - Most likely Arduino UNO")
    elif '/dev/ttyUSB0' in port:
        arduLink = '/dev/ttyUSB0'
        print("USB device found - Most likely Nano/clone")

if arduLink == ' ':
   print("Microcontroller not found, exiting")
   sys.exit()

else:
        
   piComm = serial.Serial(arduLink,19200,timeout = 2)
   piComm.flush()

# One of the items on the todo list is to integrate GPS based position using a GPS Module. This  
# fits into aims of making the rover more autonomous. How we wire in the module will depend on
# what SBC we use. Raspberry Pi's seem to lack UART ports however they do have plenty of USB ports
# mean that we would need to use a ttl adapter to bridge to the module. The Pcduino on the otherhand
# only has 1 A type USB port and an micro USB OTG port. Only the flip side, we have any of the 3
# UART ports to choose from. For the beagleBone AI I need to review the avaliable interfaces

# Raspberry Pi - if we use hardware UART, especial or newer models of Raspberry Pi then either switch 
# the Blutooth to the miniport or disable it entirely
# gpsLink = '/dev/ttyUSB0'
# gpsLink = '/dev/ttyUSB1'
# gpsLink = '/dev/ttyAMA0'

# Pcduino
# gpsLink ='/dev/ttyS1'
# LocData = serial.Serial(gpsLink,9600,timeout=2)

# data processing:
# The Microcontroller expects to recieve a command string in the format of command number, parameter1, parameter2.
# Not all commands have 2 parameters so just pass a dummy value that will be ignore on the Arduino side.

def transmit(function, param0, param1):
    
    PiCommand = [str(function),str(param0),str(param1)]
    outGoing = (','.join(PiCommand) + '\n')
    piComm.write(outGoing.encode('utf-8'))

def recieve():
    incoming = piComm.readline().decode('utf-8').rstrip()
    recievedData = incoming.split(",")
    return recievedData

# Due to the way serial is handeld on certain boards such as the leonardo we have to start the communication 
# as we have told the Arduino to wait.


mot_startup = recieve()
servo_startup = recieve()


if mot_startup[1] != motRange(0):
   print("Warning - currrent stall value does not match config, issuing overidding")
   overide_min = True

if mot_startup[2] != motRange(1):
   print("Warning - default max does not match config, overidding")
   overide_max = True

if overide_min == True:
   transmit(0, motRange(0), 0)

elif overide_max == True:
   transmit(0, 0, motRange(1))

elif overide_min and overide_max:
   transmit(0, motRange(0), motRange(1))

if servo_startup[1] != servoRange[1]:
   transmit(1, servoRange[0], 30)
   

# TODO - once we have got the control data to render correctly on the page with the
# data automatically refreshing we can then worry about handling the return data


def move_forward():
   global throttle, throttle_level, direction

   if direction != True and throttle > motRange[0]:
      stop()
      direction = True
   
   throttle = throttle_level
   return direction, throttle

def move_reverse():
   global throttle, direction

   if direction != False and throttle > motRange[0]:
      stop()
      direction = False

   throttle = throttle_level
   return direction, throttle

        
def move_left():  
   global str_pos, servoRange

   if str_pos > servoRange[1]:
      str_pos -= 5
   
   return str_pos
           
def move_right():
   global str_pos, servoRange

   if str_pos < servoRange[2]:
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
   steer_pos = move_left()
   
   return render_template('index.html', steering=steer_pos)

@app.route("/right")
def right():
   global num_mot

   print("Right")
   steer_pos = move_right()

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
# continous where the counter is disabled and the motors will keep on running until the stop command is sent. 

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
   if pan_pos < panRange[2]:
      pan_pos = panRange[2]
   
   return render_template("index.html", bearing=pan_pos)

@app.route("/panrt")
def panrt():
   global pan_pos

   print("Panrt")
   pan_pos -= 5
   if pan_pos > panRange[0]:
      pan_pos = panRange[0]
  
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
