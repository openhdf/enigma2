#!/bin/sh

cd /etc/enigma2/
echo "lamedb" > /tmp/hdf_b.cfg
ls *bouquet* >> /tmp/hdf_b.cfg
ls *.xml >> /tmp/hdf_b.cfg

echo "Backup your Bouquets/Timers/Automounts from /etc/enigma2/ to HDD"
echo
mkdir /hdd/backup 2> /dev/null
tar -czf /hdd/backup/HDF_Backup.tar.gz --files-from=/tmp/hdf_b.cfg 2> /dev/null
echo
echo "Backup complete"
echo "You can find your Backup now in /hdd/backup/HDF_Backup.tar.gz"
echo
echo