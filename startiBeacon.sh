#!/bin/bash

NUM_OCTETS=" 1E "
IBEACON_PREFIX=" 02 01 1A 1A FF 4C 00 02 15 "
NESL_UUID=" 46 A7 59 4F 67 2D 4B 6C 81 C1 78 5A EC DB A0 D5 "
MAJOR=" 00 04 "
MINOR=" 03 E7 "
POWER=" C5 "

#echo sudo hcitool -i hci0 cmd 0x08 0x0008 $NUM_OCTETS $IBEACON_PREFIX $NESL_UUID $MAJOR $MINOR $POWER 00 
sudo hcitool -i hci0 cmd 0x08 0x0008 $NUM_OCTETS $IBEACON_PREFIX $NESL_UUID $MAJOR $MINOR $POWER 00

# power up
sudo hciconfig hci0 leadv 3
sudo hciconfig hci0 noscan
