# Pcduino PWM polarity correction - In the pwm controller registers intial state 
# when the polarity bit is set to 0 the signal will be output as active low,
# which is not ideal for the driving motors as the will begining running at full
# speed uncontrollably. This is common to both the A10 and A20. This leaves us 
# with two options for setting the polarity to active high which are pwmsysfs 
# framework or write to registers directly via devmem2. In testing I didnt notice 
# much different due to the main flaw being that the adjustment is not enacted 
# until the system is nearly full booted up which takes around 2 mins or so. I 
# decided to go with the pwmsysfs being more easier to use even if it is a two 
# step process. One possible solution to reslove this is to alter the motor 
# supply so that it is only powered up once the modifications have taken place.
# A second would be a custom driver at the uboot stage that configures the
# polarity before it is handed over to the kernel

CHANNEL=0

echo $CHANNEL > /sys/class/pwm/pwmchip0/export
echo normal > /sys/class/pwm/pwmchip0/pwm$CHANNEL/polarity
