Rover Project notes:

Hardware notes-
SBC - Raspberry Pi or similar with GPIO capabilities
Arduino microcontroller - designed around Arduino Uno but will later shift to a nano or Adafruit feather
Generic DC motor (possibly replace with brushless in future)
Tower Pro Mg995 Servo for steering
2 * Buck converters (Supply for the SBC and another for the motors)
Velleman motor shield (only requires 2 pins per motor)
Lipo battery
3D printed Chasis (Mostly 3D however 2mm screws are used to hold sections together along with the wheels and drive shafts which where also purchased)
Trusty Webcam (3mp), although any usb camer or even the Pi camera could be substitued as it is merely running through mpjg-streamer

Software notes-
Flask web server - Todo figure out how to integrate with Apache web server
Arduino
Mjpg-streamer - as mentioned above
Pyserial

This is technical a combination of V1 and V2. The original project contain within this repo intially centred around using the Pcduino with some basic motor function and simple web interface featuring video feedback through a usb webcam mounted to the front of the rover. It required an adafruit Servo shield to control the main steering servo over I2C due to hardware limitations, while the main driving motor was controlled directly by one of the Pcduino's hardware PWM pins via the sysFsPwm. The problems I run into was that I could not find a way to reliably vary the speed consistantly. It either moved fairly slow or very fast with some values generating no speed. From what I later discovered when hooking the PWM pins to an oscilscope it seems that adjusting the duty cycle seems to unexpectedly alter the main period value used for generation the main frequency value to a point that the motor can no longer be driven. Therefore rather than using a vairable scale that I hoped to used I ended up stick with some presets that worked for 'slow', 'medium' and 'fast' using this instead.

The next stages in this project aim to eliminate this issues encouter previously. I decided to use an Arduino as a dedicated microcontroller that would be more capable of preforming certain task than the Pcduino. This includes driving the motors at a greater range of speeds and quickly take ultrasonic sensor readings. This frees up the SBC to instead focus more time on carrying out calculations. Due to other relaibility issues that I have encouter from a custom Armbian based OS for the Pcduino I have decided to abandonded it but I may going back to it in future depending on if I gain the experience to overcome those issues. Anyway I have no opted for the more powerful Raspberry Pi 3.
The two devices will communications over UART at a baud rate of 19200. For 3v Arduino boards, the rx and tx lines can be connected directly to the corresponding pins on the SBC rather
than USB port. 