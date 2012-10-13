#!/bin/sh

echo
echo "Please wait ... remove all WLan Drivers"
opkg remove --force-depends kernel-module-rtl8187 rtl8192cu firmware-rtl8192cu firmware-rtl8712u kernel-module-rtl2830 kernel-module-ath9k-htc kernel-module-ath9k-common kernel-module-ath9k-hw kernel-module-ath9k kernel-module-carl9170 kernel-module-zd1211rw kernel-module-ath kernel-module-rt2500usb kernel-module-rt2800lib kernel-module-rt2800usb kernel-module-rt2x00usb kernel-module-rt73usb kernel-module-rt2x00lib
rm -rf /lib/modules/3.4.3/kernel/drivers/staging/* > /dev/null 2>&1
echo
echo "Now reboot your box to unload the drivers and modules"
echo
exit 0   
