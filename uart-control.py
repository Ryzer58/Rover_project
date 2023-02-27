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
import board
import digitalio

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

last_sent = [0, 0, 0]

lit_on = False

#Light control does not have to be precise so this can simplely be toggled by the sbc with concern over the timing requirements
#Remember pins will need to be assigned base on the sbc used

#Pcduino pins:
#lamp1_pin = board.D8
#lamp2_pin = board.D9
#lamp3_pin = board.D10
#lamp4_pin = board.D11

#PI pins
lamp1_pin = board.D17
lamp2_pin = board.D27
lamp3_pin = board.D22
lamp4_pin = board.D5

fwd_lamp = digitalio.DigitalInOut(lamp1_pin)
fwd_lamp.direction = digitalio.Direction.OUTPUT
rt_lamp = digitalio.DigitalInOut(lamp2_pin)
rt_lamp.direction = digitalio.Direction.OUTPUT
lft_lamp = digitalio.DigitalInOut(lamp3_pin)
lft_lamp.direction = digitalio.Direction.OUTPUT
rev_lamp = digitalio.DigitalInOut(lamp4_pin)
rev_lamp.direction = digitalio.Direction.OUTPUT



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


def transmit(data1, data2, data3):
    piCommand = [str(data1), str(data2). str(data3)]
    toSend = (','.join(piCommand) + '\n')
    piComm.write(toSend.encode('utf-8'))


def recieve(process):

    #Reverted back to simple format, ideally this will need to streamed to process slightly different sets of data
    recieveData = piComm.readline().decode('utf-8')

    return recieveData    


myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
print (myports)

#Configure active serial port with whatever arduino type device is connected

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
motData = recieve()
motData = motData.lstrip('Motor: ')
motData = motData.split(",")
print("Motor Configuration: ")
for m in range(len(motData)):
    motParam[m] = int(motData[m])
    print(motLabel[m] + str(motData[m]))


#Fetch the Servo operating parameters and store them to the array
servoData = recieve()
servoData = servoData.lstrip('Servo: ')
servoData = servoData.split(",")

print("Servo configuaration: ")
for s in range(len(servoData)):
    servoParam[s] = int(servoData[s])
    print(servoLabel[s] + str(servoData[s]))
    
revMin, revMax, forMin, forMax = [motParam[i] for i in [0 , 1, 2, 3]]
serCentre, serLeft, serRight = [servoParam[n] for n in [0, 1, 2]]

def coreData():
    exp_angle = pos
    exp_motion = 0

    set_dir = 192 #bit 11000000
    set_turn = 48 #bit 00110000

    #Compare the infomation we just sent against what is return to ensure there are no errors
    control,motion,angle=recieve()

    control = int(control)
    motion = int(motion)
    angle = int(angle)

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

    if steer_check > 16 and exp_angle == serCentre:
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

    else:
        exp_motion = 0

    if exp_motion != motion:
       print("Error - speed does not match expected value")
       print(motion)

    #Finally check the angle against the expected one
    if exp_angle != angle:
       print("Error - angle does not match expected position")
       print(angle)


def sensorReadOut():
    #Process the sensor data - currently just using a single sensor at the front and rear for now. Later expand to using
    #an array of 3 in the format left, centre, right. One array position at the front the other at the rear
    
    dist_max = 200 #typical maximum of an ultrasonic sensor
    dist_min = 20
    #dist_turn = 80
    
    left,centre,right=recieve()

    centre = int(centre)
    right = int(right)
    left = int(left)
    
    #start of by read the centre facing sensor
    if centre < dist_min & centre != 0:
        
        c_value = str(centre)
        print("Sensors - object found within " + c_value + "cm, stopping")
        stopped()

        if right < dist_min:

            print("Suggest turn left")

        #   if right != 0:
        #       stopped() #TODO add proper avoidance handling

        # Turn left by x% based on closeness of the object
            
        if left <dist_min:

            print("Suggest turn right")

        #   if left != 0:
        #      stopped()

    else:
        print("Sensors - Not obstacles found")

#def batteryReadOut():
    #Fetch the battery levels from the 3 cells of the 11.1 Lipo battery
    
    #cell_critc = 330
    #cell_Warn = 350
    #cell_opt= 370

    #cell1,cell2,cell3=recieve()

    #if cell1 < cell_opt:

        #if cell1 <= cell_warn:

            #print("Warn battery 1 Low")

        #else:

            #Print("Critcal, begin shutdown")
            #shutdown()

    #else:
        #print("BAT 1 ok")

    #if cell2 < cell_opt:

        #if cell2 <= cell_warn:

            #print("Warn battery 2 Low")

        #else:

            #Print("Critcal, begin shutdown")
            #shutdown()

    #else:
        #print("BAT 2 ok")

    #if cell3 < cell_opt:

        #if cell3 <= cell_warn:

            #print("Warn battery 3 Low")

        #else:

            #Print("Critcal, begin shutdown")
            #shutdown()

    #else:
        #print("BAT 3 ok")

    #print("Battery level not yet supported")



try:
    while True:
        keyp = readKey()
        
        if keyp == 'w' or ord(keyp) ==16:               
            if speed < forMin: #if not already set forward the align with minimum forward vector.
                   speed = 200
                   sleep(0.5)
            print('Forward: ' + str(speed))
            run_time = 3            #start a counter to allow run time before return speed to 0 (not yet implemented)
            if lit_on == True:
                if rev_lamp == True:
                    rev_lamp = False
                fwd_lamp.value = True


        elif keyp == 's' or ord(keyp) == 17:
              if speed > revMax or speed < revMin:
                     speed = 15
                     sleep(0.5)
              print('Reverse: ' + str(speed))
              run_time = 3
              if lit_on == True:
                if fwd_lamp.value == True:
                    fwd_lamp.value = False
                rev_lamp.value = True

        elif keyp == 'd' or ord(keyp) == 19:
              print('Right:', end=' ')
              if pos < serRight:
                  pos = pos + 5
                  print(str(pos))
              if pos == serRight:
                 print('at max')
              run_time = 1 #give servo time to reach position
              if lit_on == True:
                lft_lamp.value = True
            

        elif keyp == 'a' or ord(keyp) == 18:
              print('Left:', end=' ')
              if pos > serLeft:
                  pos = pos - 5
                  print(str(pos))
              if pos == serLeft:
                  print('at max')
              run_time = 1
              if lit_on == True:
                rt_lamp.value = True

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
              
        elif keyp == 'l': #Toggle lighting on and off
            if lit_on == False:
                lit_on = True
            else:
                lit_on = False

        core_op = [speed,pos,func] #functions are work in progress so stub for now        

        transmit(core_op[0], core_op[1], core_op[2])
        coreData()
        sensorReadOut()
        #batteryReadOut()
        sleep(0.2)
       

except KeyboardInterrupt:
    reset()
    piComm.close()
    sys.exit()
