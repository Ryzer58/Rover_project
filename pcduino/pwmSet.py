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

def pulseSpeed(channel, value):
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
    """Map an angle to duty Cycle"""
    id = pwmCheck(channel)
    value = ((angle/180)*1000000)+1000000 #map out angle to duty cycle
    dutyCycle = int(value)
    #alternative aprouch
    #angleSpan = 0 - 180
    #dutySpan = 1000000 - 2000000
    #scaler = (angle - 0) / 180
    #value = 1000000 + (scaler * 1000,000)
    with open(PIN_DUTY_CYCLE % id, 'w') as f:
       f.write(str(dutyCycle))

