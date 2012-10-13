#!/bin/sh

echo
echo "delete epg & restart enigma"
sleep 3
echo "Please wait for restart Enigma!"
init 4
sleep 1
rm -f /hdd/epg.dat
sleep1
init 3
echo
echo

exit 0   
