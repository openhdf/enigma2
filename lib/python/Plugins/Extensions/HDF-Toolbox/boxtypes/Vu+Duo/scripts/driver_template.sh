#!/bin/sh

cd /tmp
echo "Download and install driver"
wget http://addons.hdfreaks.cc/et9000/driver/driver20110930_pli21.tar.gz
echo
echo "make backup"
mkdir /lib/modules/2.6.31-3.2/extra/backup
cp /lib/modules/2.6.31-3.2/extra/*.ko /lib/modules/2.6.31-3.2/extra/backup
echo
echo "extract files to:"
echo
cd /
rm -f /lib/modules/2.6.31-3.2/extra/*
tar xzvf /tmp/driver20110930_pli21.tar.gz
rm -f /tmp/driver20110930_pli21.tar.gz
echo
echo "Update Done ... Please reboot your Box now!"

exit 0   
