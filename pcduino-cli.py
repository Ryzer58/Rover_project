#basic manual control test V1

#Hardware used
#pcDuino V2 version
#Adafruit Servo / PWM Shield
#velleman Motor shield
#Buck converter
#Lipo battery
#3D printed chasis

#gps - yet to be included
#adxl - yet to be included

import time
import sys
import tty
import termios
import board
import digitalio
from pcduino import pwmSet #currently used for PWM output
from adafruit_servokit import ServoKit

#Motor 1 configuration - connect matching jumper on dir A header
#dir_1 = digitalio.DigitalInOut(board.D2)
dir_1 = digitalio.DigitalInOut(board.D4)
#dir_1 = digitalio.DigitalInOut(board.D7)
dir_1.direction = digitalio.Direction.OUTPUT

Throttle_1 = "pwm0"
speed = 60

#Motor 2 configuration - connect matching jumper on dir B header
#dir_2 = digitalio.DigitalInOut(board.D8)
#dir_2 = digitalio.DigitalInOut(board.D12)
#dir_2 = digitalio.DigitalInOut(board.D13)
#dir_2.direction = digitalio.Direction.OUTPUT

#Throttle_2 = "pwm1"

#Servo positions
centre = 30
right = 60
left = 0

#configure lighting controls
Hd_lamps = digitalio.DigitalInOut(board.D8)
Hd_lamps.direction = digitalio.Direction.OUTPUT
#Ind_Lft = (connect to 555 timer)
#Ind_rt =
#Rear =

def mot_setup():
    pwmSet.pulseDuration(Throttle_1, 25000000) #Period value in nanoseconds
    pwmSet.pulseDuty(Throttle_1, 0) #start at a stationary position
    pwmSet.polarity(Throttle_1, 0) #Not strictly necessary as it should already be set 0 using the correction script
    pwmSet.enable(Throttle_1, 1)

    dir_1.value = True #set throttle to in Direction A

    #like the Arduino the Pcduino has an 8 bit PWM counter which can produce an array of frequencies but the PWM sysFS
    #specifices time in nano seconds rather than the period. (commas are for readability only)
    # 1KHz - 1,000,000
    # 500Hz - 2,000,000
    # 400Hz - 2,500,000
    # 250Hz - 4,000,000
    # 200Hz - 5,000,000


def servo_setup():
    pos = centre
    kit = ServoKit(channels=16) #setup steering servo
    kit.servo[0].angle = pos

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
       pwmSet.pulseDuty(Throttle_1, 0)
       pwmSet.enable(Throttle_1, 0)
 
       raise KeyboardInterrupt
    return ch

def readKey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c2
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65) #16=Up, 17=Down, 18=Right, 19=Left arrows

mot_setup()
servo_setup()


try:
    while True:
          keyp = readKey()
          if keyp == 'w' or ord(keyp) ==16:
               dir_1.value = True
               print('Forward')
               pwmSet.pulseDuty(Throttle_1, speed)
               time.sleep(1)
               pwmSet.pulseDuty(Throttle_1, 0)

          elif keyp == 's' or ord(keyp) == 17:
                 dir_1.value = False #set gpio Low to change direction
                 print('Reverse')
                 pwmSet.pulseDuty(Throttle_1, speed)
                 time.sleep(1)
                 pwmSet.pulseDuty(Throttle_1, 0)

          elif keyp == 'd' or ord(keyp) == 19:
                 if pos > left:
                    pos = pos - 5
                 if pos == left:
                    print('max limit reached')
                 kit.servo[0].angle = pos
                 time.sleep(0.5) #give servo time to reach position
                 print('turn left', pos)

          elif keyp == 'a' or ord(keyp) == 18:
                 if pos < right:
                    pos = pos + 5
                 if pos == right:
                    print('max limit reached')
                 kit.servo[0].angle = pos
                 time.sleep(0.5)
                 print('turn right', pos)

          elif keyp == '.' or keyp == '>':
                 speed = min(100, speed+10)
                 print ('Accel', speed)

          elif keyp == ',' or keyp == '<':
                 speed = max(0, speed-10)
                 print ('Deccel', speed)
          
          elif keyp == 'k' or ' ':
               pwmSet.pulseDuty(Throttle_1, 0)
               pwmSet.enable(Throttle_1, 0)
               raise KeyboardInterrupt
               
          elif keyp == 'l': #Toggle On/Off the Main head lamps
            if Hd_lamps == True:
                Hd_lamps.value = False
            else:
                Hd_lamps.value = True


except KeyboardInterrupt:
    raise KeyboardInterrupt
    sys.exit
