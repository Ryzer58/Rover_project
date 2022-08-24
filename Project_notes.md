Rover Project notes:

Hardware notes-
SBC - Raspberry Pi or similar with GPIO capabilities
Arduino microcontroller - designed around Arduino Uno but will later shift to a nano or Adafruit feather
Generic DC motor (possibly replace with brushless in future)
Tower Pro Mg995 Servo for steering
2 * Buck converters - Supply for the SBC and another for the motors)
Velleman motor shield - only requires 2 pins per motor
Lipo battery
3D printed Chasis - Optional, can be done with any frame that support a servo for forward steering
Trusty Webcam (3mp) - although any usb camer or even the Pi camera could be substitued as it is merely running through mpjg-streamer

Software notes-
Flask web server - Todo figure out how to integrate with Apache web server
Arduino
Mjpg-streamer - as mentioned above (Add camStream.sh to start to run as a service at boot in the 'init' folder)
Pyserial

Pcduino version only-

Adafruit ciruitPython
Adafruit Servo kit

The frame:
Much like the electronics side of things this is also in the process of evolving. Intially I intended to have almost all of the rover 3D printed. The very first frame I made even had 3d printed wheels. So that the main components sat nicely in my print printbed, they where subdivided into sections and joined together with 2mm screws.This caused two problems, the first that the wheels where too small which made navigating certain obstacles difficult but could have been improved by enlarging them. However this may not necessarily cure the second issue of traction/grip as the wheels would sometimes slip. Now I currently use a set of rubber wheels that are aproximately 65mm diameter, while not perfect the do offer much better traction (still need to test outside). The main drive shafts used are 3mm and the gears used in the motor drive assembly come an MFA Come drills kit. mean while the actual motor frame was 3D and also contributed to the drive issues as I found the gears to be fairly tight. Adjustments have now been made and the gears now spin a lot more freely but there is still some fine tuning to do. The front wheels are simply steered by a bar connected to the main servo. currently there is no suspension so to speak of other than some springs on the front wheels that provide partial dampening. The main body still needs to be finalised. Once it is at a suitable stage I will most likely upload it to Thingverse. Admittedly I could have probably saved my self a lot of hassle by purchasing a pre-designed frame and assembly which I do have some already but these are mostly of the fixed wheel type rather than the steerable design that I was looking for.

This is technical a combination of V1 and V2. The original project contain within this repo intially centred around using the Pcduino with some basic motor function and simple web interface featuring video feedback through a usb webcam mounted to the front of the rover. It required an adafruit Servo shield to control the main steering servo over I2C due to hardware limitations, while the main driving motor was controlled directly by one of the Pcduino's hardware PWM pins via the sysFsPwm. The problems I run into was that I could not find a way to reliably vary the speed consistantly, where trying to adjust increment or decrement the duty cycle it did not behave in the expected pattern. An instance being that setting it to what should be 50% duty yielded no movement. Basically it seemed fairly random. From what I later discovered when hooking the PWM pins to an oscilscope it seems that adjusting the duty cycle seems to strangely alter the main period value. This in some cases lead to frequencies that where to high for the motor to turn. Therefore rather than using a vairable scale that I hoped to used I ended up stick with some presets that worked for 'slow', 'medium' and 'fast' using some values that I discovered to work within these profiles. Further digging from the tools I found seem suggest a period completely different to the one I used, but the problem with that was I could not get any output with that value.. Interestingly the problem is the not present on the Pcduino3 which indicates a problem writing to the registers correctly. This will probably require a custom driver fix which I will try to work on.

The next stages in this project aim to eliminate this issues encouter previously. I decided to use an Arduino as a dedicated microcontroller that would be more capable of preforming certain task than the Pcduino. This includes driving the motors at a greater range of speeds and quickly take ultrasonic sensor readings. This frees up the SBC to instead focus more time on carrying out calculations. Due to other relaibility issues that I have encouter from a custom Armbian based OS for the Pcduino I have decided to abandonded it but I may going back to it in future depending on if I gain the experience to overcome those issues. Anyway I have no opted for the more powerful Raspberry Pi 3.
The two devices will communications over UART at a baud rate of 19200. For 3v Arduino boards, the rx and tx lines can be connected directly to the corresponding pins on the SBC rather
than USB port. 