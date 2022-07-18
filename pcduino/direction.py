#!/usr/bin/python
#for use with the velleman motor shield otherwise use LN2993 chip direct
#By setting the pin state as high or low will determine the direction of
# the motor
#Under this approuch the direction is set by placing one of the two pins
#high and the other low to move in one direction or vice versa to move 
#in the opposite direction
VALID_GPIO_PINS = ('gpio2', 'gpio4','gpio7','gpio8','gpio12','gpio13')

PIN_LOCATE = '/sys/class/gpio/%s/'
PIN_SETUP = '/sys/class/gpio/%s/direction'
PIN_STATE ='/sys/class/gpio/%s/value'

OUTPUT = 'out'
FOR = 1
BAC = 0
INPUT = 0

class InvalidChannelException(Exception):
    """channel not suported"""
    pass

def getValidId(channel):
   if channel in VALID_GPIO_PINS:
     return channel #later to look into a configuration option for setup without board
   else:
     raise InvalidChannelException

#def setDualPin(chan_1, chan_2)
#To add next for manual configuration when using connecting to the chip directly
#dirA = getValidId(chan_1)
#dirB = getValidId(chan_2)
#with open(PIN_SETUP % dirA, 'w') as f:
#f.write('out')
#f.close
#with open(PIN_SETUP % dirB, 'w') as f:
#f.write('out')
def setPin(channel):
     """Set the Mode of gpio channel"""
     id = getValidId(channel)
     with open(PIN_SETUP % id, 'w') as f:
         f.write('out')

def setMot(channel, value):
     """set pin the direction of the chip"""
     id = getValidId(channel)
     with open(PIN_STATE % id, 'w') as f:
        f.write('1' if value == FOR else '0')

#def setDual(chan_1, chan_2, dir)
#"""Manual configuration for H-bridge driver"""
#dirA  = getValidId(chan_1)
#dirB = getValidId(chan_2)
#with open(PIN_STATE % dirA, 'w') as f:
#f.write('1' if dir == FOR else '0')
#f.close
#with open(PIN_STATE % dirB, 'w') as f:
#f.write('0' if dir == FOR else '1')
#f.close
