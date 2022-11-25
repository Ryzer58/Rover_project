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
from pcduino import pwmSet # currently used for PWM output
from adafruit_servokit import ServoKit

#Motor 1 configuration - Match with the jumper set on dir A header, to control motor direction
#dir_1 = digitalio.DigitalInOut(board.D2)
dir_1 = digitalio.DigitalInOut(board.D4)
#dir_1 = digitalio.DigitalInOut(board.D7)
dir_1.direction = digitalio.Direction.OUTPUT

Throttle_1 = "pwm0" # Pcduino hardware PWM channel (pin D5). 
speed = 60

#Motor 2 configuration - Match with the jumper set on dir B header, to control motor direction
#dir_2 = digitalio.DigitalInOut(board.D8)
#dir_2 = digitalio.DigitalInOut(board.D12)
#dir_2 = digitalio.DigitalInOut(board.D13)
#dir_2.direction = digitalio.Direction.OUTPUT

# Throttle_2 = "pwm1" # Pcduino pin D6, On the velleman motor shield this brought out next to D5 on the PWMA
# header therefore a jumper wire will need to bridge from the D6 pin to the PWMB header to be able to us the
# second motor channel on the pcduino

# Servo positions
centre = 30
right = 60
left = 0

pos = centre
kit = ServoKit(channels=16) #setup steering servo
kit.servo[0].angle = pos

# configure lighting controls
Hd_lamps = digitalio.DigitalInOut(board.D8)
Hd_lamps.direction = digitalio.Direction.OUTPUT
#Ind_Lft = digitalio.DigitalInOut(board.D9)
#Ind_Lft.direction = digitalio.Direction.OUTPUT - To do, think of way to make blink
#Ind_rt = digitalio.DigitalInOut(board.D10)
#Ind_rt.direction = digitalio.Direction.OUTPUT
#Rear = digitalio.DigitalInOut(board.D11)
#Rear .direction = digitalio.Direction.OUTPUT


pwmSet.pulseDuration(Throttle_1, 400) # Enter frequecency (smallest value is 200hz)
pwmSet.pulseDuty(Throttle_1, 0) #start at a stationary position
pwmSet.enable(Throttle_1, 1)

dir_1.value = True #set throttle to in Direction A

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

          elif keyp == 'a' or ord(keyp) == 19:
                 if pos > left:
                    pos = pos - 5
                 if pos == left:
                    print('max limit reached')
                 kit.servo[0].angle = pos
                 time.sleep(0.5) #give servo time to reach position
                 print('turn left', pos)

          elif keyp == 'd' or ord(keyp) == 18:
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
    
    sys.exit()
