#Basic opreation control test between the Raspberry Pi and Arduino microcontroller
#Hardware used
#Raspberry Pi B 2/3
#Arduino Uno
#velleman Motor shield
#Tower Pro MG 995 Servo
#Buck converter
#Lipo battery
#3D printed chasis

from operator import truediv
from shutil import move
from time import sleep
import serial
import serial.tools.list_ports
import sys
import tty
import termios

#Variables to store the control data feteched from the Arduino

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
func = 0

speedLock = 0

#Search and configure any active serial port

myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
print (myports)


for port in myports:
    if '/dev/ttyACM0' in port:
        arduLink = '/dev/ttyACM0'
        print("ACM device found - Most likely Arduino UNO")
    elif '/dev/ttyUSB0' in port:
        arduLink = '/dev/ttyUSB0'
        print("USB device found - Most likely Nano/Clone")
    else:
        print("Error - Arduino not detected")
        
piComm = serial.Serial(arduLink,19200,timeout = 3)
piComm.flush()


#Fetch the motor operating parameters and store results
motor = piComm.readline().decode('utf-8').lstrip('Motor: ') # Excluding motor label left for debugging directly with serial monitor
motData = motor.split(",")
print("Motor Configuration: ")
for m in range(len(motData)):
    motParam[m] = int(motData[m])
    print(motLabel[m] + str(motData[m]))

#Fetch the Servo operating parameters and store results
servo = piComm.readline().decode('utf-8').lstrip('Servo: ')
servoData = servo.split(",")
print("Servo configuaration: ")
for s in range(len(servoData)):
    servoParam[s] = int(servoData[s])
    print(servoLabel[s] + str(servoData[s]))
    
revMin, revMax, forMin, forMax = [motParam[i] for i in [0 , 1, 2, 3]]
serCentre, serLeft, serRight = [servoParam[n] for n in [0, 1, 2]]


def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
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
    
    
def reset():
    reset = ['0','30','0']
    transmit()


def stopped():
    stopping = ['0',str(pos),'0',]
    transmit()

#Core data handlers for recieving and transmitting

def transmit():
    toSend = (','.join(PiCommand) + '\n')
    piComm.write(toSend.encode('utf-8'))


def recieve():
    recieve = piComm.readline().decode('utf-8').rstrip()
    recieveData = recieve.split(",")
    return recieveData


#Returned data functions

def returnedInput():
    exp_angle = pos
    exp_motion = 0
    #Compare the infomation we just sent against what is return to ensure there are no errors
    control, motion,angle = recieve()

    #first check the control, need to convert the value back into raw bits, only first 4 used
    #Need to figure out how to compare bits properly

    #second check the actual raw accelaration value, excluding direction
    if speed <= 185:
        exp_motion = speed + 70

    elif speed >= 190:
        exp_motion = speed - 115

    if exp_motion != int(motion):
        print("speed error")
    
    #Finally check the angle against the expected one
    if exp_angle != int(angle):
        print("steering error")

def sensorReadOut():
    #Process the sensor data - currently just using an array of ultrasonics divided into 2
    #groups of an array of 3 in the format left, centre, right
    print("Sensors - Not yet supported")

def batteryReadOut():
    #Fetch the battery levels in format cell1, cell2, cell3
    print("Battery level not yet supported")



try:
    while True:
        keyp = readKey()
        
        if keyp == 'w' or ord(keyp) ==16:               
            if speed < forMin: #if not already set forward the align with minimum forward vector.
                   speed = 200
                   sleep(0.5)
            print('Forward: ' + str(speed))
            run_time = 3            #start a counter to allow run time before return speed to 0 (not yet implemented)


        elif keyp == 's' or ord(keyp) == 17:
              if speed > revMax or speed < revMin:
                     speed = 15
                     sleep(0.5)
              print('Reverse: ' + str(speed))
              run_time = 3

        elif keyp == 'd' or ord(keyp) == 19:
              print('Right:', end=' ')
              if pos < serRight:
                  pos = pos + 5
                  print(str(pos))
              if pos == serRight:
                 print('at max')
                 run_time = 1 #give servo time to reach position

        elif keyp == 'a' or ord(keyp) == 18:
              print('Left:', end=' ')
              if pos > serLeft:
                  pos = pos - 5
                  print(str(pos))
              if pos == serLeft:
                  print('at max')
                  run_time = 1

        elif keyp == '.' or keyp == '>':
              print('Accelarating', end=' ')
              if speed >= revMin and speed < revMax: #Reverse Accelration
                  speed = speed + 10
                  print('in reverse to ' + str(speed))

              elif speed >= forMin and speed < forMax: #Forward Accelration
                  speed = speed + 10
                  print('forward to ' + str(speed))

              elif speed == 0:
                   print('stationary')
              
              else:
                   print('at max speed')

        elif keyp == ',' or keyp == '<':
            print('Deccelarating', end=' ')
            if speed > revMin and speed <= revMax: #Reverse Accelration
                  speed = speed - 10
                  print('in reverse to ' + str(speed))
                  
            elif speed > forMin and speed <= forMax: #Forward Accelration
                  speed = speed - 10
                  print('forward to ' + str(speed))
            
            elif speed == 0:
                 print('stationary')
                 
            else:
                print('at min speed')
          
        elif keyp == 'e' or '/':
              print('Stopping')
              preSpeed = speed
              speed = 0
              
        elif keyp == 'l': #Only main working function is lighting
            if func != 10:
                func = 10
            else:
                func = 0

        PiCommand = [str(speed),str(pos),str(func)] #functions are work in progress so stub for now
        
        returnedInput()
        sensorReadOut()
        batteryReadOut()


except KeyboardInterrupt:
    reset()
    piComm.close()
    sys.exit()