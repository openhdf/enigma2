#!/bin/sh

echo "Restore your Bouquets/Timers/Automounts from HDD to /etc/enigma2/"
echo

if [ -f /hdd/backup/HDF_Backup.tar.gz ]; then 
	echo "Backup found ... restore now"
	cd /etc/enigma2
	rm -f *bouquet*
	rm -f lamedb
	rm -f automounts.xml
	rm -f *timer*
	tar xzf /hdd/backup/HDF_Backup.tar.gz
	echo
	echo "Restore complete"
	echo "Please wait ... restart GUI"
	sleep 5
	init 4
	sleep 1
	init 3
	echo
	echo
else
	echo "No backup /hdd/backup/HDF_Backup.tar.gz found!"
	echo "Can't restore old data"
	echo
fi
exit 0 