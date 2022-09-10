#!/usr/bin/env python

_PIN_FD_PATH = '/sys/bus/iio/devices/iio:device1/in_voltage%s_raw'

#Caution the devices seems to be device 0 on newer kernels

def analog_read(channel):
    """Return the integer value of an adc pin.

    adc0 and adc1 have 6 bit resolution, in additon to have a voltage limit of 2.0V. The two LRADC are normal 
    connected to buttons aranged as part of a voltage ladder whereby the voltage in mv is used to identify the 
    button pushed. There is not a mechanism to get raw readings from these inputs other than the framework for 
    dealing with button presses. Only the very old Linksprite stock images include them as part of the adc 
    package. Having said that it should be possible to write a driver to abstract the raw values form the data 
    registers should a suitable use case be found but for now just read the main TP adc lines. 
    
    adc2 through adc5 have a 12 bit resolution as well as being capable of reading the full voltage range of
    3.3V. It appears to be fine if only reading one line at a time such as with a temperature sensor albiet I
    am not entirely sure about the accuracy of the readings, it is possible that some kind of offset factor
    may be required to produce more accurate results. Reading multiple lines appears to create a senario where
    the system thinks its overheating it shutdowns in repsonse to a critcal temperate alert. The same control
    that reads these inputs also has a 5th internal connection that reads the CPU's temperature. The thing is
    that the controller has two modes of operation. The first being a four wire mode in which the temperature
    probe is configured to read the temperature. The second mode is a raw adc where each of the pins are 
    measured seperately which is what this framework reads. It seems that to the driver switched between these
    modes in an attempt to provide flexibility.

    """


    with open(_PIN_FD_PATH % channel, 'r') as f:
        return int(f.read(33))
