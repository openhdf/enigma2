#!/bin/sh

cd /tmp
echo "Download and install driver"
wget http://addons.hdfreaks.cc/et9000/driver/driver_et6x00_01022012.tar.gz
echo "make backup"
mkdir /lib/modules/3.2.2/extra/backup 2> /dev/null
cp /lib/modules/3.2.2/extra/*.ko /lib/modules/3.2.2/extra/backup
echo
echo "extract files to:"
cd /
rm -f /lib/modules/3.2.2/extra/* 2> /dev/null
tar xzvf /tmp/driver_et6x00_01022012.tar.gz 2> /dev/null
rm -f /tmp/driver_et6x00_01022012.tar.gz
echo
echo "Update Done ... Please reboot your Box now!"
echo
exit 0   
