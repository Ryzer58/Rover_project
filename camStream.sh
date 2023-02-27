#!/bin/sh

# A script to start mjpeg-streamer service, which will need to be called form by refering to it from Rc.lcoal. The primry target  is the USB Trusty webcam so it is not biased to working on
# the PI only. Depending on the SBC used the video source number seems to change this will need to be kept in mind. I may change over to the Pi Camera when using the PI, so the reference 
# video source will need to be changed to correspond to the correct video source. Ideally I would like to add some kind of auto detection in future. In relation to running on different SBC's
# it may be possible to use the internal system files to predict the right video source. It may prove an additional commplication to then employ detect for if the USB camera is plugged in
# or the PI camera is avaliable given that the initialization will need to be changed from 'input_uvc' to 'raspi_cam'

PORT="8080"
SIZE="640x480"
FRAMERATE="10" #30 is the max fps for the Trust webcam

export LD_LIBRARY_PATH=/usr/local/LD_LIBRARY_PATH
mjpg_streamer -i "input_uvc.so -f $FRAMERATE -r $SIZE -d /dev/video1 -y" -o "output_http.so -w /var/www/html -p $PORT"
