#!/bin/sh

PORT = "8080"
SIZE = "480X360"
FRAMERATE="10"

export LD_LIBRARY_PATH=/usr/local/LD_LIBRARY_PATH
mjpg_streamer -i "input_uvc.so -f $FRAMERATE -r $SIZE -d /dev/video1 -y" -o "output_http.so -w /var/www/html -p $PORT"

#For PI video0 should be fine but in the case of the Pcduino video1 tends to the normal source