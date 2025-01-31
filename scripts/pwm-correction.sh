# Sunxi PWM polarity correction - In the PWM controller register a single bit
# is used to control the polarity of the signal output. The default state for
# both channels is active low. This is definitely the casefor the Allwinner 
# A10 and A20 but could differ on newer hardware. For certain applications 
# such as driving an LED backlight this is fine but in the case of driving 
# motors until corrected the PWM output is uncontrolled and at full speed.
# 
# PWM is interfaced using the standard sysfsPWM framework and therefore we need
# to first export the channel before we can use it. Then we can set the polarity 
# into 'normal' state. Ideally this should happen as soon as possible while
# booting however currently there is a noticeable time delay before this script
# is called during which period there is no control of the PWM output.
#
# Todo - Investigate better workarounds/improvements. One possibility is to replace
# the controller board with a newer or custom motor driver featuring a dedicated
# enable pin. A second option would be to add some form of power isolation on the
# motor supply side to prevent any motion until PWM is properly set. Going down the
# software route would involve alterations to the existing sun4i PWM driver to add
# a node for configuring the polarity within the dts. 


CHANNEL=0

echo $CHANNEL > /sys/class/pwm/pwmchip0/export
echo normal > /sys/class/pwm/pwmchip0/pwm$CHANNEL/polarity
