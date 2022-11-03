#Basic opreation control test between the Raspberry Pi and Arduino microcontroller
#Hardware used
#Raspberry Pi B 2/3
#Arduino Uno
#velleman Motor shield
#Tower Pro MG 995 Servo
#Buck converter
#Lipo battery
#3D printed chasis

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

fwd_offset = 115
rev_offset = 70

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


def recieve(process):

    if process == 0:
        motor = piComm.readline().decode('utf-8').lstrip('Motor: ') #filter out debug label to return only configuration values

    if process == 1:
        servo = piComm.readline().decode('utf-8').lstrip('Servo: ')

    else:
        toRecieve = piComm.readline().decode('utf-8').rstrip()
    recieveData = toRecieve.split(",")
    return recieveData    


def returnedInput():
    exp_angle = pos
    exp_motion = 0

    set_dir = 192 #bit 11000000
    set_turn = 48 #bit 00110000

    #Compare the infomation we just sent against what is return to ensure there are no errors
    control,motion,angle=recieve(2)

    
    #first check the control, which is configure in bits to see roughly if the rover is 
    # behaving as expected.

    dir_check = control & set_dir

    if dir_check == 0 and speed != 0:
        print("Error - not in motion")

    elif dir_check != 0 and speed == 0:
        print("Error - not stopped")

    if dir_check == set_dir and speed < forMin:
        print("Error - not driving forward")

    elif dir_check == 128 and speed > revMax:
        print("Error - not driving in Reverse")


    #See if we are turn and which way we are turning
    steer_check = control & set_turn

    if steer_check != 30 and exp_angle == serCentre:
        print("Error - steering not Centred")

    elif steer_check == set_turn and exp_angle < serCentre:
        print("Error - failed to turn Right")

    elif steer_check == 32 and exp_angle > serCentre:
        print("Error - failed to turn Left")

    
    #second check the actual raw accelaration value, excluding direction
    if speed <= 185:
       exp_motion = speed + rev_offset

    elif speed >= 190:
       exp_motion = speed - fwd_offset

    if exp_motion!=int(motion):
       print("Error - speed does not match expected value")
       print(motion)

    #Finally check the angle against the expected one
    if exp_angle!=int(angle):
       print("Error - angle does not match expected position")
       print(angle)


def sensorReadOut():
    #Process the sensor data - currently just using a single sensor at the front and rear for now. Later expand to using
    #an array of 3 in the format left, centre, right. One array position at the front the other at the rear
    
    dist_max = 200
    dist_min = 20
    #dist_turn = 80
    
    left,centre,right=recieve(3)
    
    if centre < dist_min:
        #Stop if the minimum threshold limit is reached
        stopped()

        #if right < dist_min or left <dist_min:
        #Suggest turning in a free direction
        #   if right < dist_min:
            #suggest turning left
            #if left < dist_min:

        #if right < dist_min and left < dist_min:
            #stopped
    
    print("Sensors - Not yet supported")

def batteryReadOut():
    #Fetch the battery levels in format cell1, cell2, cell3
    
    #cell1,cell2,cell3=recieve(4)
    print("Battery level not yet supported")



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


#Fetch the motor operating parameters and store them to the array
motData = recieve(0)
print("Motor Configuration: ")
for m in range(len(motData)):
    motParam[m] = int(motData[m])
    print(motLabel[m] + str(motData[m]))


#Fetch the Servo operating parameters and store them to the array
servoData = recieve(1)
print("Servo configuaration: ")
for s in range(len(servoData)):
    servoParam[s] = int(servoData[s])
    print(servoLabel[s] + str(servoData[s]))
    
revMin, revMax, forMin, forMax = [motParam[i] for i in [0 , 1, 2, 3]]
serCentre, serLeft, serRight = [servoParam[n] for n in [0, 1, 2]]


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
        
        returnedInput()
        sensorReadOut()
        batteryReadOut()
        sleep(0.2)
       

except KeyboardInterrupt:
    reset()
    piComm.close()
    sys.exit()
