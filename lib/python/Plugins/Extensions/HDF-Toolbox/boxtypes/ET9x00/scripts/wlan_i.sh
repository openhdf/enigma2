#!/bin/sh

echo
echo "Please wait ... install all WLan drivers"
opkg install firmware-rtl8192cu firmware-rtl8712u kernel-module-rtl2830 kernel-module-rtl8187 rtl8192cu kernel-module-ath9k-htc kernel-module-ath9k-common kernel-module-ath9k-hw kernel-module-ath9k kernel-module-carl9170 kernel-module-zd1211rw kernel-module-ath kernel-module-rt2500usb kernel-module-rt2800lib kernel-module-rt2800usb kernel-module-rt2x00usb kernel-module-rt73usb kernel-module-rt2x00lib
echo
echo "Now reboot your box to load the drivers and modules"
echo
exit 0