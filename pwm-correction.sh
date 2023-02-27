# Pcduino PWM polarity correction - In its intial state the Hardware is active low,
# which is not ideal for the motor driving shield as it leads to the motors 
# constantly spinning at full speed with no means of control. Therefore we first
# need to export the channel that we will use to allow as to access the api, the
# we can configure the polarity in 'normal' to switch it into active high.
# A limitation of this approuch is that there is a notable delay before this script
# appears to be excuted from RC.local

CHANNEL = 0

echo $CHANNEL > /sys/class/pwm/pwmchip0/export
echo normal > /sys/class/pwm/pwmchip0/pwm$CHANNEL/polarity
