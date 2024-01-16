Rover Project notes:

Hardware notes:
SBC - Raspberry Pi but also tested on the Pcduino2. The end goal is for a flexible approuch
that can easily be adapted to work any SBC
Microcontroller - Arduino Uno (Atmega328) but later plan to switch to Adafruit feather due 
to the more compact for factor or maybe the Arduino Nano
Motor - Generic DC motor Brushed motor
Velleman motor shield - only requires 2 pins per motor channel (direction and pwm out)
Servo - Tower Pro Mg995, if using 1 it is always allocated to steering first unless the 2 
motor configuration is used.
Detection - 6 * HC-SR04 Ultrasonic sensors
Power - 3 Cell LIPO battery
2 * Buck converters - At a minimum we need a seperate supply for our SBC and another for the 
motors. Ideally the sensors should aslo have their own isolated supply.
Chasis - 3D printed Chassis, or use a pre-built frame. This origionally intended to be used 
with a rack and pinion system but will be adapted to support differential drive as the next 
milestone.
Camera - Trusty Webcam (3mp), although any usb camera or Pi camera module if using the 
Raspberry 
Adafruit Servo/PWM Shield - If using just an SBC on its own, it may have limited PWM capable 
like the Pcduino2 then it is best to have external hadware to control any attached Servos.
The Shield is communicated with via I2C.


Software notes:
Flask web server - (WIP, currently has a basic working interface)
Arduino IDE
Adafruit Blinka/Circuitpython - Makes it easy to interface with external components
Adafruit Servo kit - A library to allow us to interface with our servos
Mjpg-streamer - as mentioned above (Add camStream.sh to start to run as a service at boot in the 'init' folder)
Pyserial - Allows python to interface with serial devices


The frame:
This is currently a WIP in progress, Once it is a more finalize state I will either include in the repo or upload to 
Thingiverse. It would have been easier to start with a kit but very rarely have I come across a frame which implemnents
rack and pinion steering, usually they are just use differential drive. I have used the Velleman K8400 to print out the 
majority of parts with PLA fliment. As some parts ended up exceeding the build volume they have been split smaller 
sections. This has the added benefit of carrying out localized upgrades rather than having to print out the entire frame
each time.
parts where it was impratical to print due to scale where most sourced from Amazon. The drive assembly mechanisms come 
from the MFA Come drills kit. The main drive shaft 3mm diameter as well as those used on the steering assembly. All parts 
are bound together using 2mm diameter screws although the length of these vary. Again the width used will be specified
at a later data. 
For now the Servo is mounted directly above the steering rack but one of the future ambitions is to move it forward and
introduce some form of foward suspension. There are some weaknes in the current steering frame that need to be addressed
although it may be additional strength once more of the body panels are in place. The driver assembly is currently the
main focus with the motor housing being overhauled as well as slight alterations to the gear assembly to accomodate a
larger motor.
Rather than printing wheels like I did on a prototype Rover that I made ages ago, I have used wheels from the Kit
mentioned above which seem to prefrom ok but I did have to glue them to drive shaft as the did develope a tendency
to slip.


The Project:

This project was started with the goal of seeing how feasible it would be to use a Pcduino 2 as the brains of a Rover. While not exactly an Arduino, mostly just copying the form factor. The oirginal OS did have it's own version of the Arduino IDE but I was unable to get it to work with external libraries plus the OS itself is now very outdate. It allowed for addtional pins to be used as PWM at the expense of CPU cycles. Running Armbian OS allowed it to run more up to date software althogh it may be offical EOL
the buildscriptsd make it easy to produce an up to date OS. Using Adafruit Blinka made it very easy to inferface with external hardware. The only other alternative is to use Raspberry Pi that has masses more support. So far it seems able to handle running a
web server as well as streaming video output from the USB webcam.

The first major challenge was with the PWM, while it has 2 channels the combination of prescalers and 8-bit resolution meant that its ablity to driver a servo was extremly limted. To Solve this the adafruit Servo shield was added, communicating with the Pcduino
over I2C. Now I had at atleast drivable Rover but had problems adjusting the speed of the drive motor. By a process of trail and error I was able to find values that would near enough yield the desired result but the speed would not scale linearly. Another draw back was the was the polarity configuration. By default the state is active low, meaning the pin will be held high. A basic but not ideal solution to this was to create an rc.local script to export the pin and set the polarity. Later on I discovered that the problem was with how the driver handle the hardware. It is design for numerous Allwinner chips that share the same underlying PWM hardware registers. Except from the A10 they all suppotrt 16-bit resolution however the driver assumed all SOCs support this resolution. It resulted in situtation where whatever was written to the period regsiter, the upper 8-bits are simply ignore resulting in unexpected behaviour. To rectify this the driver need to be patched so that in the case of the A10 it would only write into the lower 8-bits for both the total cycles and active duty. The patch was applied to a rebuilt kernel. Further improvements could be achieved in either hardware or software. The hardware option would invovle withholding power from the motors until the PWM has been configure correctly, using an additional gpio to toggle the supply. The software solution requires additional tweaks to the driver functionality that could allow for polarity to be assigned within the device tree.

The second challenge was configuring a web control interface afer passing the test of the basic control programme which is controlled purely by keypresses. They easy part was getting the video stream displayed on the webpage thanks to mjpeg-streamer running in the backgroud. The problematic part which still is in need of improvement was the position of elements on the page to match the intended layout. Based on early experiments a set of predefine speed values have been assigned to 'radio' buttons for selection which
cover 'slow', 'medium' and 'fast'. This next stage here will be instead switch to a sliding bar to act more like a conventional accelerator aside from this other improvements are just asthetics.

Introduce an Arduino microcontroller as a much easier solution to problems relating to PWM, along with sensor readings. Communications take place over uart at a baud rate of 19200 for the time being. Other options I may look into is communicating over SPI, possibly introducing a second microcontroller if need. The Rover seemed to struggle on softer surfaces so to overcome this the old motor has 
been replaced with a much larger one.
Currently Data with the exeception of setup is sent in the format of Command Number, Data1, Data2. For now the command number just sets the direction of the Rover but have started overhauling to cover over functions. To allow the Rover to behave more autonomously an array of 3 distance sensors has been added to the front and Rear of the Rover body. This is the current goal being proactively worked.
