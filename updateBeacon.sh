sudo hcitool -i hci0 cmd 0x08 0x000a 00
sleep 0.1
sudo hcitool -i hci0 cmd 0x08 0x0008 1F 02 02 02 02 02 02 02 02 02 02 02 02 02 02 02 02
sleep 0.1
sudo hcitool -i hci0 cmd 0x08 0x000a 01

# make 100 ms
#sudo hcitool -i hci0 cmd 0x08 0x0006 A0 00 A0 00 03 00 00 00 00 00 00 00 00 07 00
# power up
#sudo hcitool -i hci0 cmd 0x08 0x000a 01
