#!/bin/sh

PORT="8080"
SIZE="640x480"
FRAMERATE="10" #30 is the max fps for the Trust webcam

export LD_LIBRARY_PATH=/usr/local/LD_LIBRARY_PATH
mjpg_streamer -i "input_uvc.so -f $FRAMERATE -r $SIZE -d /dev/video1 -y" -o "output_http.so -w /var/www/html -p $PORT"

#For PI video0 should be work in most case
#The Pcduino on the otherhand tends to be located at video1 as video is reserved for the hdmi display buffer