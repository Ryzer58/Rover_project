#!/bin/sh

# A script to start mjpeg-streamer service. Either the contents should be copied into Rc.lcoal or a link pointing to this file added. To maintain some flexiblity to change between platforms
# I have included a device option that can simply be changed depending the camera used. In reality this will only make a difference on the PI as the other SBCs do not have a camera connection
# port. Another thing to consider is that video source differs depending on the SBC used. For some reason this no longer seems to work, need to do a bit more digginh into bash scripts. Ideally
# once working, try to figure out how to implement somekind of auto detection feature.

PORT="8080"
SIZE="640x480"
FRAMERATE="10" #30 is the max fps for the Trust webcam
DEVICE = "input_uvc.so" #"raspi_cam.so"
SOURCE = "video1"


export LD_LIBRARY_PATH=/home/ryan/mjg-streamer/mjpg-streamer-experiemental
./mjpg_streamer -i "$DEVICE -f $FRAMERATE -r $SIZE -d /dev/$SOURCE" -o "output_http.so -w ./www -p $PORT"
