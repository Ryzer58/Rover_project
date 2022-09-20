Rover Project notes:

Hardware notes-
SBC - Raspberry Pi or similar with GPIO capabilities
Arduino microcontroller - designed around Arduino Uno but will later shift to a nano or Adafruit feather
Generic DC motor (possibly replaced with brushless in future)
Tower Pro Mg995 Servo for steering
2 * Buck converters - Supply for the SBC and another for the motors)
Velleman motor shield - only requires 2 pins per motor
Lipo battery
3D printed Chassis - Optional, can be work with wheeled steering frame that support a servo for forward steering
Trusty Webcam (3mp) - although any usb camera or even the Pi camera could be substitued as it is merely running through mpjg-streamer

Software notes-
Flask web server - Todo figure out how to integrate with Apache web server
Arduino
Mjpg-streamer - as mentioned above (Add camStream.sh to start to run as a service at boot in the 'init' folder)
Pyserial

Pcduino version only-

Adafruit ciruitPython
Adafruit Servo kit

The frame:
This is currently a WIP in progress, in future I may decide to upload the documents to either github or Thingiverse. Admittedly it would probably been easier to start with a pre-made kit but very rarely have I come across a frame with a steering control, usually they are just
differential drive. Parts are currently printed out of PLA on Vertex K8400. To keep within the limits of the print bed, the model was broken into sections. These sections are joined together with 2mm screws. To overcome issues with earlier design 65mm diameter rubber wheels are used, connected to a 3mm drive shaft at the back. They appear to have reasonably good traction but sometimes struggle at low speed on carpet and I have yet to test handling outside. The gears used are part of the MFA Come drills kit. The drive assembling being the current area that is actively being tweaked with. The front wheels are simply steered by the main servo. currently there is no suspension so to speak of other than some springs on the front wheels that provide partial dampening.

The Project:

This is technical a combination of V1 and V2. The original project contain within this repo initially centred around using the Pcduino with some basic motor function and simple web interface featuring video feedback through a usb webcam mounted to the front of the rover. It required an adafruit Servo shield to control the main steering servo over I2C due to PWM's hardware limitations, while the main driving motor was controlled directly by one of the Pcduino's hardware PWM pins via the PWM sysFS. At the time I found it to be difficult to get the output duty cycle to vary properly. Connecting to an oscilloscope it was trail and error
to input a value that would produce the desired frequency, worser still I could not get the duty cycle to behave as expected and it would also end up causing the main frequency to jump.
This was not ideal for controlling a motor where the resultant value would be to high a frequency for the motor to turn. Evidently this was symptoms of an underlying issue with the driver.
For the web interfaces it was just a case of find numbers that worked near enough to what I was expecting and using to create a set of predefine profiles that where 'slow', 'medium' and 'fast'.
Examining the driver as part of a separate goal of my to learn more about the internals of Linux, I was able to identify and fix the issue so that overall the PWM behaves as expected with the inputted period value now result in the desired frequency. The does remain one minor issue to work around but in the case it is due to how the hardware is actually formatted. In the default state, the polarity of any PWM channel is active low. This means that when no signal is being generated the pin will linger high, unfortunately a side effect of this will be that It will cause the motor to move until the pin is set to a low state. A short term fix is a small polarity correction script to flip the palority but this wont be called until later on the in the boot process so the motor will run continuous for a minute or so until this has been executed. Ideally this is another factor that will need to be accounted for in the driver in future or via an additional pre-configuration driver situated in u-boot.

In this next stage of the project I aim to change the design to a hybrid model by including an Arduino microcontroller to handle certain task. At the moment this involved driving the motors and taking ultrasonic sensor readings. This frees up the SBC to instead focus more time on carrying out calculations. Communication will be carried out over UART at a baud rate of 19200, although I may look into switching to I2C in future.
Aside from the PWM the Pcduino does have a few other problems to address which may be resolved in time along with being much less powerful than the more popular Raspberry Pi. Going forward I will probably be working the Raspberry Pi 3 more but occasionally revisiting the Pcduino. The advantages of the Pcduino compared to the PI is the greater number of uart ports which are much more compacted than USB ports although you have to be cautious of the voltage difference.
