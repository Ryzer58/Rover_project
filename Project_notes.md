Rover Project notes:

Hardware notes:
SBC - Raspberry Pi but also tested on the Pcduino2. It should work on any board that has suitable IO capabilities
Microcontroller - Arduino Uno but later plan to switch to Adafruit feather due to its more compact for factor or maybe the Arduino Nano
Motor - Generic DC motor (possibly replaced with brushless in future)
Velleman motor shield - only requires 2 pins per motor channel (direction and pwm out)
Tower Pro Mg995 Servo for steering
Detection - 6 * HC-SR04 Ultrasonic sensors
Power - 3 Cell LIPO battery
2 * Buck converters - Supply for the SBC and another for the motors
3D printed Chassis - Optional, can be work with wheeled steering frame that support a servo for forward steering
Trusty Webcam (3mp) - although any usb camera or even the Pi camera could be substitued as it is merely running through mpjg-streamer


Software notes:
Flask web server - Todo figure out how to integrate with Apache web server
Arduino ide - optional, for making quick fixes.
Adafruit Blinka/Circuitpython
Mjpg-streamer - as mentioned above (Add camStream.sh to start to run as a service at boot in the 'init' folder)
Pyserial
Adafruit Servo kit - When using the Pcduino 2 the hardware PWM is not capble of controlling a Servo. Therefore control is managed by the shield using I2C communication


The frame:
This is currently a WIP in progress, in future I may decide to upload the documents to either github or Thingiverse. Admittedly it would probably been easier to start with a pre-made kit but very rarely have I come across a frame with a steering control, usually they are just based around differential drive. I have used the Velleman K8400 to print out the majority of parts with PLA fliment. As some parts ended up becoming fairly large they have been divide into sections to fit within the limits of the
Printed bed. The remainder parts come from the MFA Come drills kit and from Amazon. Parts are bound with 2mm diameter screws of varying lengths. The steel shafts used in the drive assembly are 3mm diameter. For now the Servo is mounted directly above the steering rack but this may change when proper suspension is introduced in the next reprint. The driver assembly is currently being reworked to support the upgrade to a lager drive motor. The problem with the previous was that outside of the control issues
it appear to struggle running on soft surfaces, granted this may also be in part due the level of friction on the wheels.


The Project:

This project was started with the goal of seeing how feasible it would be to use a Pcduino 2 as the brains of a Rover. While not exactly an Arduino, mostly just copying the form factor. The oirginal OS did have it's own version of the Arduino IDE but I was unable to get it to work with external libraries plus the OS itself is now very outdate. It allowed for addtional pins to be used as PWM at the expense of CPU cycles. Running Armbian OS allowed it to run more up to date software althogh it may be offical EOL
the buildscriptsd make it easy to produce an up to date OS. Using Adafruit Blinka made it very easy to inferface with external hardware. The only other alternative is to use Raspberry Pi that has masses more support. So far it seems able to handle running a
web server as well as streaming video output from the USB webcam.

The first major challenge was with the PWM, while it has 2 channels the combination of prescalers and 8-bit resolution meant that its ablity to driver a servo was extremly limted. To Solve this the adafruit Servo shield was added, communicating with the Pcduino
over I2C. Now I had at atleast drivable Rover but had problems adjusting the speed of the drive motor. By a process of trail and error I was able to find values that would near enough yield the desired result but the speed would not scale linearly. Another draw back was the was the polarity configuration. By default the state is active low, meaning the pin will be held high. A basic but not ideal solution to this was to create an rc.local script to export the pin and set the polarity. Later on I discovered that the problem was with how the driver handle the hardware. It is design for numerous Allwinner chips that share the same underlying PWM hardware registers. Except from the A10 they all suppotrt 16-bit resolution however the driver assumed all SOCs support this resolution. It resulted in situtation where whatever was written to the period regsiter, the upper 8-bits are simply ignore resulting in unexpected behaviour. To rectify this the driver need to be patched so that in the case of the A10 it would only write into the lower 8-bits for both the total cycles and active duty. The patch was applied to a rebuilt kernel. Further improvements could be achieved in either hardware or software. The hardware option would invovle withholding power from the motors until the PWM has been configure correctly, using an additional gpio to toggle the supply. The software solution requires additional tweaks to the driver functionality that could allow for polarity to be assigned within the device tree.

The second challenge was configuring a web control interface afer passing the test of the basic control programme which is controlled purely by keypresses. They easy part was getting the video stream displayed on the webpage thanks to mjpeg-streamer running in the backgroud. The problematic part which still is in need of improvement was the position of elements on the page to match the intended layout. Based on early experiments a set of predefine speed values have been assigned to 'radio' buttons for selection which
cover 'slow', 'medium' and 'fast'. This next stage here will be instead switch to a sliding bar to act more like a conventional accelerator aside from this other improvements are just asthetics.

Introduce an Arduino microcontroller as a much easier solution to problems relating to PWM, along with sensor readings. Communications take place over uart at a baud rate of 19200 but in future I may consider swicthing over to SPI depending on what situational
challenges arise. Data is sent in the format of Command Number, Data1, Data2. For now the command number just sets the direction of the Rover but will be expanded later. To allow the Rover to behave more autonomously an array of 3 distance sensors has been added to the front and Rear of the Rover body. This is the current goal being proactively worked.
