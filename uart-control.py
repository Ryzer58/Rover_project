# Basic opreation control test between the Raspberry Pi and Arduino microcontroller
# Hardware used
# Raspberry Pi B 2/3
# Arduino Uno
# velleman Motor shield
# Tower Pro MG 995 Servo
# Buck converter
# Lipo battery
# 3D printed chasis

from time import sleep
import serial
import serial.tools.list_ports
import sys
import tty
import termios
import board
import digitalio

# Variables to store the control data feteched from the Arduino

min_throttle = 0
max_throttle = 0
mot_dir = 0
motParam = [min_throttle, max_throttle]
motLabel = ['Min throttle ', 'Max throttle ']
throttle = 0

servo_right = 0
servo_centre = 0
servo_left = 0
servoParam = [servo_centre, servo_left, servo_right]
servoLabel = ['Centre ','Max left ','Max right ']
pos = 30

#func = 0

speedLock = 0

last_sent = [0, 0, 0]

lit_on = False

# Light control does not have to be precise so this can simplely be toggled by the sbc with concern over the timing requirements
# Remember pins will need to be assigned base on the sbc used

# Pcduino pins:
#lamp1_pin = board.D8
#lamp2_pin = board.D9
#lamp3_pin = board.D10
#lamp4_pin = board.D11

# PI pins
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
    reset = [0,0,30]
    transmit(reset[0], reset[1], reset[2])


def stopped():
    stopping = [mot_dir,0,pos,]
    transmit(stopping[0], stopping[1], stopping[2])


def transmit(data1, data2, data3):
    piCommand = [str(data1), str(data2), str(data3)]
    toSend = (','.join(piCommand) + '\n')
    piComm.write(toSend.encode('utf-8'))


def recieve():

    # Reverted back to simple format, ideally this will need to streamed to process slightly different sets of data
    recieveData = piComm.readline().decode('utf-8')

    return recieveData    


myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
print (myports)

# Configure active serial port depend arduino type device is connected. The only limitation of this approuch is the 
# case of the board being disconnected the reconnected that could make it register as 'ACMx' or 'ttyUSBx'

for port in myports:
    if '/dev/ttyACM0' in port:
        arduLink = '/dev/ttyACM0'
        print("ACM device found - Most likely Arduino UNO")
    elif '/dev/ttyUSB0' in port:
        arduLink = '/dev/ttyUSB0'
        print("USB device found - Most likely Nano/clone")

        
piComm = serial.Serial(arduLink,19200,timeout = 2)
piComm.flush()


# Fetch the configuration data then store to arrays as allocated above
configData = recieve()
configData = configData.split(';') # Seperate the motor from the Servo constraints
motData, servoData = configData

# Start by processing the Motor data
motData = motData.lstrip('Motor: ')
motData = motData.split(',')
print('Motor Configuration: ')
for m in range(len(motData)):
    motParam[m] = int(motData[m])
    print(motLabel[m] + str(motData[m]))

# Now proccess data retaining the Servo
servoData = servoData.lstrip(' Servo: ')
servoData = servoData.split(',')

print("Servo configuaration: ")
for s in range(len(servoData)):
    servoParam[s] = int(servoData[s])
    print(servoLabel[s] + str(servoData[s]))

min_throttle, max_throttle = [motParam[i] for i in [0 , 1]]
servo_centre, servo_left, servo_right = [servoParam[n] for n in [0, 1, 2]]

def coreData():
    exp_angle = pos
    exp_throttle = throttle

    mov_for = 192   # bits 11000000
    mov_rev = 128  # bits 10000000
    turn_right = 48 # bits 00110000
    turn_left = 32  # bits 00100000

    #Compare the infomation we just sent against what is return to ensure there are no errors
    posData = recieve()
    posData = posData.split(",")
    control = posData[0]
    motion = posData[1]
    angle = posData[2]

    control = int(control)
    motion = int(motion)
    angle = int(angle)

    # first check the control, by inspecting the bits to check that the Rover is 
    # working as expected. There are currently issue when attempting a turn seems
    # to lead to a drive error which could be a false positive or a sign of a deeper
    # routed issue

    dir_check = control & mov_for

    if dir_check == 0 and throttle != 0:
        print("Drive Error - not moving")

    elif throttle == 0:
        if dir_check != 0 and mot_dir == 0:
            print("Drive Error - not stopped")
        
        if dir_check != 64 and mot_dir == 1:
            print("Drive Error - not stopped")

    
    elif throttle != 0:
        if dir_check != mov_for and mot_dir == 1:
            print("Drive Error - not driving forward")
            print(dir_check)

        elif dir_check != mov_rev and mot_dir == 0:
            print("Drive Error - not driving in Reverse")
            print(dir_check)

    if exp_throttle != motion:
       print("Drive Error - throttle should be " + str(exp_throttle) + " but returned " + str(motion))


    # See if we are turn and which way we are turning
    steer_check = control & turn_right

    if steer_check > 16 and exp_angle == servo_centre:
        print("Error - steering not Centred")

    elif steer_check == turn_right and exp_angle < servo_centre:
        print("Error - failed to turn Right")

    elif steer_check == turn_left and exp_angle > servo_centre:
        print("Error - failed to turn Left")

    if exp_angle != angle:
       print("Steer Error - angle should be set to " + str(exp_angle) + " but returned " + str(angle))
       


def sensorReadOut():
    # Process the sensor data - currently just using a single sensor at the front and rear for now. Later expand to using
    # an array of 3 in the format left, centre, right. One array position at the front the other at the rear
    
    dist_max = 200 # typical maximum of an ultrasonic sensor
    dist_min_upper = 5
    dist_min_lower = 2
    #dist_turn = 80
    
    senData  = recieve()
    senData = senData.split(",")
    left,centre,right= senData

    centre = int(centre)
    right = int(right)
    left = int(left)
    
    #start of by read the centre facing sensor
    if centre < dist_max:
        
        if centre > dist_min_upper:
           c_value = str(centre)
           print("Sensors - Warning object found within " + c_value + "cm")

        if centre < dist_min_upper and centre > dist_min_lower:
           stopped()
           print("Sensors - Stopping object found directly in front of path")

        if right < dist_min_upper and right > left:

            print("Suggest turn right")

        #   if right != 0:
        #       stopped() #TODO add proper avoidance handling

        # Turn left by x% based on closeness of the object
            
        if left <dist_min_upper and left > right:

            print("Suggest turn left")

        #   if left != 0:
        #      stopped()

    else:
        print("Sensors - Not obstacles found")

#def batteryReadOut():
    # Fetch the battery levels from the 3 cells of the 11.1 Lipo battery
    
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
            if mot_dir != 1:
                mot_dir = 1
                throttle = min_throttle # Reset to lowest speed if changing direction
            elif throttle == 0:
                throttle = min_throttle
                sleep(0.5)
            print('Forward: ' + str(throttle))
            if lit_on == True:
                if rev_lamp == True:
                    rev_lamp = False
                fwd_lamp.value = True


        elif keyp == 's' or ord(keyp) == 17:
            if mot_dir !=0:
                mot_dir = 0
                throttle = min_throttle
            elif throttle == 0:
                throttle = min_throttle
                sleep(0.5)
            print('Reverse: ' + str(throttle))
            run_time = 3
            if lit_on == True:
                if fwd_lamp.value == True:
                    fwd_lamp.value = False
                rev_lamp.value = True

        elif keyp == 'd' or ord(keyp) == 19:
            print('Turning right:', end=' ')
            if pos < servo_right:
                pos = pos + 5
            if pos < servo_centre:
                print('now bearing left at ' + str(pos))
            if pos == servo_centre:
                print('now centred')
            else:
                print('now at ' + str(pos))
            if pos == servo_right:
                print('at max')
            if lit_on == True:
                lft_lamp.value = True
            

        elif keyp == 'a' or ord(keyp) == 18:
            print('Turning left:', end=' ')
            if pos > servo_left:
                pos = pos - 5
            if pos > servo_centre:
                print('now bearing right at ' + str(pos))
            if pos == servo_centre:
                print('now centred')
            else:
                print('now at ' + str(pos))
            if pos == servo_left:
                print('at max')
            if lit_on == True:
                rt_lamp.value = True

        elif keyp == '.' or keyp == '>':
            if throttle < max_throttle and throttle >= min_throttle:
                print('Accelarating', end=' ')
                throttle = throttle + 10
                if mot_dir == 1:
                    print(' forward to ' + str(throttle))
                else:
                    print(' in reverse to ' + str(throttle))

            elif throttle == 0:
                 print('Currently idle')

            else:
                print('Set to max throttle')
                
                  
        elif keyp == ',' or keyp == '<':
            if throttle > min_throttle:
                print('Deccelarating', end=' ')
                throttle = throttle - 10
                if mot_dir == 1:
                    print(' forward to ' + str(throttle))
                else:
                    print(' in reverse to ' + str(throttle))

            elif throttle == 0:
                 print('Currently idle')

            else:
                print('Set to min throttle')  
          
        elif keyp == 'e' or '/':
              print('Stopping')
              throttle = 0
              
        elif keyp == 'l': # Toggle lighting on and off
            if lit_on == False:
                lit_on = True
            else:
                lit_on = False

        core_op = [mot_dir,throttle,pos] # functions are work in progress so stub for now        

        transmit(core_op[0], core_op[1], core_op[2])

        if core_op[0] != last_sent[0] or core_op[1] != last_sent[1] or core_op[2] != last_sent[2]:
            coreData() # only read back if we are sending any new data 
        
        last_sent[0] = core_op[0]
        last_sent[1] = core_op[1]
        last_sent[2] = core_op[2]

        sensorReadOut()
        #batteryReadOut()
        sleep(0.2)
       

except KeyboardInterrupt:
    reset()
    piComm.close()
    sys.exit()
