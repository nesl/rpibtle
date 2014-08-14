#!/bin/bash

NUM_OCTETS=" 1F "
IBEACON_PREFIX=" 02 01 1A 1A FF 4C 00 02 15 "
NESL_UUID=" 46 A7 59 4F 67 2D 4B 6C 81 C1 78 5A EC DB A0 D5 "
MAJOR=" 00 04 "
MINOR=" 03 E7 "
POWER=" C5 "

#echo sudo hcitool -i hci0 cmd 0x08 0x0008 $NUM_OCTETS $IBEACON_PREFIX $NESL_UUID $MAJOR $MINOR $POWER 00 
sudo hciconfig hci0 up
#sudo hcitool -i hci0 cmd 0x08 0x0008 $NUM_OCTETS $IBEACON_PREFIX $NESL_UUID $MAJOR $MINOR $POWER 00
sudo hcitool -i hci0 cmd 0x08 0x0008 1F 01 AA 1C 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31

# power up
#sudo hciconfig hci0 leadv 3
#sudo hciconfig hci0 noscan

# make 100 ms
sudo hcitool -i hci0 cmd 0x08 0x0006 A0 00 A0 00 03 00 00 00 00 00 00 00 00 07 00

# power up
sudo hcitool -i hci0 cmd 0x08 0x000a 01


