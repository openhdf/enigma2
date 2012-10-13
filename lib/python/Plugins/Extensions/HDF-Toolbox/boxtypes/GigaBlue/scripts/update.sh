#!/bin/sh
echo "Download new version"
IP=hdfreaks.cc
ping -c 1 $IP
if [ $? == 0 ]
	then
		wget http://addons.hdfreaks.cc/HDF-Toolbox/release.tgz -O /usr/lib/enigma2/python/Plugins/Extensions/release.tgz
	else
  		echo "update failed"
fi;

if [ -f /usr/lib/enigma2/python/Plugins/Extensions/release.tgz ]; then 
	rm -f /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/samba/* > /dev/null 2>&1
	rm -f /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/* > /dev/null 2>&1
	rm -f /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/menu/* > /dev/null 2>&1
	rm -f /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/* > /dev/null 2>&1
	cp /usr/lib/enigma2/python/Plugins/Extensions/release.tgz /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/release.tgz
	cd /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox
	tar xzf release.tgz
	rm release.tgz
	rm /usr/lib/enigma2/python/Plugins/Extensions/release.tgz
	date > /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.lastupdate.log
echo
echo
echo "please reboot enigma now"
echo
echo
else
	echo "sorry there is a problem"
fi
exit 0 
