#!/bin/sh

target=`cat /proc/mounts | grep -m 1 net | cut -d" " -f2`

if [ -z $target ]
	then
	echo "No net mount found to use for speedtest ... exit"
	echo
	exit
fi

echo "speedtest use first mount = $target"
echo

echo "speedtest $target ~ 50MB ... please wait"
time dd if=/dev/zero of=$target/blanks2 bs=1024k count=50
rm $target/blanks2
echo

#echo "speedtest $target ~ 100MB ... please wait"
#time dd if=/dev/zero of=$target/blanks2 bs=1024k count=100
#rm $target/blanks2
#echo

echo "speedtest $target ~ 200MB ... please wait"
time dd if=/dev/zero of=$target/blanks2 bs=1024k count=200
rm $target/blanks2
echo

exit 0   
