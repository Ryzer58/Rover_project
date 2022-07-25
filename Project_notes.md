Rover Project notes:

Hardware Notes-
SBC - Raspberry Pi or similar with GPIO capabilities
Arduino microcontroller - designed around Arduino Uno but will later shift to a nano or Adafruit feather
Generic DC motor (possibly replace with brushless in future)
Tower Pro Mg995 Servo for steering
2 * Buck converters (Supply for the SBC and another for the motors)
Velleman motor shield (only requires 2 pins per motor)
Lipo battery
3D printed Chasis (Mostly 3D however 2mm screws are used to hold sections together along with the wheels and drive shafts which where also purchased)

This is technical a combination of V1 and V2. The original project contain within this repo intially centred around using the Pcduino with some basic 
motor function and simple web interface featuring video feedback. It required an adafruit Servo shield to control the main steering servo over I2C and
the main driver motor was controlled directly by one of the Pcduino's hardware PWM pins via the sysFsPwm. The problems that I run into was that I was
unable to get a reliable way to vary the speed consistantly, it either moved fairly slow or very fast with some values generating no speed. From what
I could test it seems that adjusting the duty cycle seems to cause some unexpected behaviour by also adjusting the main period values which then 
becomes either two high or two low for the motor.

The next stages in this project aim to eliminate this issues by passing certain task to an Arduino and expand the functionality of the rover. All
communications will be made over UART. For 3v Arduino boards, the rx and tx lines can be connected directly to the corresponding pins on the SBC rather
than USB port. The motors and ultrasonic sensor readings will be carried out on the Arduino and then passed onto the SBC for more complex processing.
