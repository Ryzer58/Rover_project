# Pcduino PWM polarity correction - In the PWM controller register a single bit
# is used to control the polarity of the signal output. In its default state of 
# 0 the signal is active low. This is ok for driving something such as LCD
# Backlight but not motors, resulting in the motor spinning uncontrollably at
# full speed. This seems to be the case for both the Allwinner A10 and A20.
# This script is designed to set the PWM into the 'normal' polarity state as
# soon as the system has booted, which unfortunately takes over a minute.
# This into account there was unoticeable difference between setting the bit
# directly with devmem tool versus simply using two steps involved under the
# pwmsysfs framework. 
# In future a possible solution would be to alter/upgrade the motor controller 
# board to allow us to simply isolate the motor power supply until the polarity 
# bit has been set.
# A second would be customise the driver as a more advance work around although
# this could risk breaking compatibility with the pwmsysfs framework which we
# would like to retain.

CHANNEL=0

echo $CHANNEL > /sys/class/pwm/pwmchip0/export
echo normal > /sys/class/pwm/pwmchip0/pwm$CHANNEL/polarity
