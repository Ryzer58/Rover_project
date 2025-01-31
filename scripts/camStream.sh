#!/bin/bash

# A script to start mjpeg-streamer service. Either the contents can be copied into rc.local directly or 
# invoke this script from rc.local. Ideally this should be universal however different hardware have
# differing video devices meaning that we would need a mechanism to identify the board and then if the
# expected device is avaliable. This is complicated on platforms like the Raspberry Pi where the camera
# can be mounted to the CSI or USB port. Other SBCs like the Beaglebone Ai can only have a USB camera
# connection. 

PORT="8080"
SIZE="640x480"
FRAMERATE="10" # Adjust according to capabilites of the camera/CPU utilization (Trust webcam max = 30)
DEVICE="input_uvc.so" 
SOURCE="video1" # for now manual adjust for hardware used


export LD_LIBRARY_PATH=/usr/local/lib
mjpg_streamer -i "$DEVICE -f $FRAMERATE -r $SIZE -d /dev/$SOURCE" -o "output_http.so -w /usr/local/share/mjpg-streamer/www -p $PORT"


exit
