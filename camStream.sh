#!/bin/bash

# A script to start mjpeg-streamer service. Either the contents should be copied into Rc.lcoal or a link pointing to this file added. To maintain some flexiblity to change between platforms
# I have included a variable for setting the input device. At some point I would like to make this condition based where by examine something like the OS release can be used to predicted
# what port would be used. In addtion there is a device variable which is mainly for use on the PI as other Hardware I current have does not have a readily
# available camera port. 

PORT="8080"
SIZE="640x480"
FRAMERATE="10" #30 is the max fps for the Trust webcam
DEVICE="input_uvc.so" #"raspi_cam.so"
SOURCE="video1" #"video0"


export LD_LIBRARY_PATH=/usr/local/bin
mjpg_streamer -i "$DEVICE -f $FRAMERATE -r $SIZE -d /dev/$SOURCE" -o "output_http.so -w /usr/local/share/mjpg-streamer/www -p $PORT"

exit
