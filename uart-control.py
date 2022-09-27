#Basic opreation control test between the Raspberry Pi and Arduino microcontroller
#Hardware used
#Raspberry Pi B 2/3
#Arduino Uno
#velleman Motor shield
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

for port in myports:
    if '/dev/ttyACM0' in port:
        arduLink = '/dev/ttyACM0'
        print("ACM device found - Most likely Arduino UNO")
    elif '/dev/ttyUSB0' in port:
        arduLink = '/dev/ttyUSB0'
        print("USB device found - Most likely Nano")
    else:
        print("Error - Arduino not detected")
        
piComm = serial.Serial(arduLink,19200,timeout = 2)
#piComm = serial.Serial('/dev/ttyUSB0',19200,timeout = 2) #For compitability with Nano clones (CH304)
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
#revMin = motParam[0]
#revMax = motParam[1]
#forMin = motParam[2]
#forMax = motParam[3]

#serCentre = servoParam[0]
#serLeft = servoParam[1]
#serRight = servoParam[2]

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

def transmit():
    toSend = (','.join(PiCommand) + '\n')
    piComm.write(toSend.encode('utf-8'))

def recieve():
    toRecieve = piComm.readline().decode('utf-8').rstrip()
    recieveData = toRecieve.split(",")
    
    #todo - need to include a proper handler function to split data then process according to type
    
    #DataSet1 -core data:

    #segment1 - status byte:
    #use to confirm if we are moving and in what direction
    #still need to learn how to disect the desired results then store appropriately
    #remember to covert from a string to a byte
    

    #untested - need to upgrade arduino sketch once chasis body modifications are made
    #
    #move =  128
    #forward = 64
    #turning = 32
    #right = 16
    #
    #motion = int(recieveData[0]) & move
    #
    #if motion == move:
    #    moving = True
    #
    #   dir = recieveData[0] & forward
    #
    #   if dir == forward:
    #       goForward = True
    #       #add in error check
    #
    #   else:
    #       goForward = False
    #
    #else:
    #   moving = False
    #
    #pivot = recieveData[0] & turning
    #
    #if pivot == turning:
    #
    #   turn = True
    #   swing = recieveData[0] & right
    #
    #   if swing == right:
    #
    #       goRight = True
    #
    #   else:
    #       goRight = False
    #
    #else:
    #
    #   turn = False
    #
    #segment2 - raw throttle data
    #As we already know the direction this will instead return a direction PWM based on the sketch mapping
    #then calculate what the value should be based on the original vector to confirm
    #In the future this will probably be combind with additional sensor data such as speed 
    #
    #segment3 - servo position
    #This will just confirm that it has recieved the value we have expected it to.
    #
    #if recieveData[2] != pos:
    #   
    #    print("Steering error")
    #
    #Dataset2 - Ultrasonic sensor data:
    # probably do this in a second pass and think of a more organised way to handle
    #
    #segements 1 - 3 - Readings from the array of sensorys, this will either be the forward or rear array, use status byte to
    # identify which array is being sourcesed from.


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
        
        transmit()
        
        recieve()
       

except KeyboardInterrupt:
    reset()
    piComm.close()
    sys.exit()
    

    
