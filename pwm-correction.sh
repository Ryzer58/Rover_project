# Sunxi PWM polarity correction - In the PWM controller register a single bit
# is used to control the polarity of the signal output. In unset state the
# pulse is active low, which is ok for use casses such as LED backlight but 
# not for this application of driving motors. This is definetly the case for
# the Allwinner A10 and A20 but I have not tested on newer chips. This is a
# simple fix to set the polarity into 'normal' as soon as possible when booting.
# A limitation of this approach is that it takes around a minute to come into
# effect, during which time the motors are spinning uncontrollably at full power.
# A future a possible solution would be replace the motor controller with a 
# different chip that has a proper hardware enable pin which is not set until
# the polarity has been configured. We could also add addition hardware that
# isolates the motor power. Ideally it would be better if we could pre-configure
# the polarity within the dts overlay but this is a more complex challenge that
# would involve a rewrite of the sun4i-pwm driver. 


CHANNEL=0

echo $CHANNEL > /sys/class/pwm/pwmchip0/export
echo normal > /sys/class/pwm/pwmchip0/pwm$CHANNEL/polarity
