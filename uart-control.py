#Basic opreation control test between the Raspberry Pi and Arduino microcontroller
#Hardware used
#Raspberry Pi B 2/3
#Arduino Uno
#velleman Motor shield
#Buck converter
#Lipo battery
#3D printed chasis

from time import sleep
import serial
import sys
import tty
import termios
#import thread - Time control fail safe mechanism to add later.

pos = 30
speed = 0
wait_time = 0
func = 0

preSpeed = 0

piComm = serial.Serial('/dev/ttyACM0',19200,timeout = 1)
#piComm = serial.Serial('/dev/ttyUSB0',19200,timeout = 1) #For compitability with Nano clones (CH304)
#Any improvement may be to read the paramters from the arduino and


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
    feedback = piComm.readline().decode('utf-8').rstrip()
    print(feedback)
    #Still need to find a more useful way to handle incoming data
    


try:
    while True:
        keyp = readKey()
        
        if keyp == 'w' or ord(keyp) ==16:               
            if speed < 190: #if not already set forward the align with minimum forward vector.
                   speed = 200
                   sleep(0.5)
            print('Forward: ' + str(speed))
            run_time = 3            #start a counter to allow run time before return speed to 0 (not yet implemented)


        elif keyp == 's' or ord(keyp) == 17:
              if speed > 185 or speed < 5:
                     speed = 15
                     sleep(0.5)
              print('Reverse' + str(speed))
              run_time = 3

        elif keyp == 'd' or ord(keyp) == 19:
              print('Right')
              if pos < 60:
                  pos = pos + 5
              if pos == 0:
                 wait_time = 1 #give servo time to reach position

        elif keyp == 'a' or ord(keyp) == 18:
              print('Left')
              if pos > 0:
                  pos = pos - 5
              if pos == 60:
                  wait_time = 1

        elif keyp == '.' or keyp == '>':
              print('Accelarating')
              if speed >= 5 and speed <= 185: #Reverse Accelration
                  speed = speed + 10
              elif speed >=190 and speed <370: #Forward Accelration
                  speed = speed + 10
              else:
                   print('Max speed')

        elif keyp == ',' or keyp == '<':
            print('Deccelarating')
            if speed > 5 and speed < 185: #Reverse Accelration
                  speed = speed - 10
            elif speed > 190 and speed < 370: #Forward Accelration
                  speed = speed - 10
            else:
                print('Min speed')
          
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
    
except IOError:
    print("Adruino not detected")
    
