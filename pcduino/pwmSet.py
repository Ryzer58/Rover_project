import os.path
import math
HARD_PWM_PINS = ('pwm0', 'pwm1')
SOFT_PWM_PINS = ('gpio3', 'gpio9','gpio10','gpio11')

PIN_MAP = "/sys/devices/platform/soc@01c00000/1c20e00.pwm/pwm/pwmchip0/%s"
PIN_DUR = "/sys/devices/platform/soc@01c00000/1c20e00.pwm/pwm/pwmchip0/%s/period"
PIN_DUTY_CYCLE = "/sys/devices/platform/soc@01c00000/1c20e00.pwm/pwm/pwmchip0/%s/duty_cycle"
SET_ENABLE = "/sys/devices/platform/soc@01c00000/1c20e00.pwm/pwm/pwmchip0/%s/enable"
SET_POLARITY = "/sys/devices/platform/soc@01c00000/1c20e00.pwm/pwm/pwmchip0/%s/polarity"

DISABLE = 0

class InvalidChannelException(Exception):
      """The channel selected is not a dedicated pwm pin"""
      pass

def pwmCheck(channel):
    if channel in HARD_PWM_PINS:
        return channel
    elif channel in SOFT_PWM_PINS:
        print("Warning soft channel selected, may not be as accurate as required")
        return channel
    else:
        raise InvalidChannelException

def pulseDuration(channel, freq):
    """write the total duration to period file"""
    id = pwmCheck(channel)
    with open(PIN_DUR % id, 'w') as f:
        f.write(str(freq))

    #Currently broken via sysFs on A10

def pulseDuty(channel, value):
    """set the duty cycle"""
    freq = 0
    id = pwmCheck(channel)
    with open(PIN_DUR % id, 'r') as f:
         freq = f.read()
    period = int(freq)
    rep = (value /255)*period
    level = int(rep)
    f.close
    with open(PIN_DUTY_CYCLE % id, 'w') as f:
        f.write(str(level))
        

def enable(channel, use):
    """to enable the pwm"""
    id = pwmCheck(channel)
    with open(SET_ENABLE % id, 'w') as f:
        f.write('0' if use == DISABLE else '1')

def polarity(channel, dir):
    """To correctly configure the polarity"""
    id = pwmCheck(channel)
    with open(SET_POLARITY % id, 'w') as f:
        f.write('inveresed' if dir == 1 else 'normal')

def servo(channel, angle):
    """Map the angle to an appropriate duty cycle [works on Pcduino3 only] - Servos typical require a duty cycle of 5 (1.0ms) to 10%(2.0ms), confirm with servo datasheet"""
    id = pwmCheck(channel)
    
    value = 0(angle/180)*2000000
    
    #alternative aprouch
    angleSpan = 0 - 180
    dutySpan = 1000000 - 2000000
    scaler = (angle - 0) / 180
    value = 1000000 + (scaler * 1000,000)
    
    
    # duty num | width | Angle - resoltion 9 degrees, possibly 1.8
    #  2000000    2.0    180
    #  1950000    1.95   171                
    #  1900000    1.9    162            
    #  1850000    1.85   153
    #  1800000    1.8    144
    #  1750000    1.75   135
    #  1700000    1.70   126
    #  1650000    1.65   117
    #  1600000    1.6    108
    #  1550000    1.55    99         
    #  1500000    1.5     90 
    #  1450000    1.45    81
    #  1400000    1.4     72
    #  1350000    1.35    63
    #  1300000    1.3     54
    #  1250000    1.25    45 
    #  1200000    1.2     36 
    #  1150000    1.15    27 
    #  1100000    1.1     18  
    #  1050000    1.05    9
    #  1000000    1.0     0
    dutyCycle = int(value)
    with open(PIN_DUTY_CYCLE % id, 'w') as f:
       f.write(str(dutyCycle))

#def softPwm
#To implement later
