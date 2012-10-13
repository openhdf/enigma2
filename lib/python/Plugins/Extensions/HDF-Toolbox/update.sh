#!/bin/sh
echo "Download new version"
IP=hdfreaks.cc
ping -c 1 $IP  > /dev/null 2>&1
if [ $? == 0 ]
	then
		wget http://addons.hdfreaks.cc/HDF-Toolbox/release.tgz -O /usr/lib/enigma2/python/Plugins/Extensions/release.tgz
		echo "download complete"
	else
  		echo "update failed"
fi;

if [ -f /usr/lib/enigma2/python/Plugins/Extensions/release.tgz ]; then 
	rm -fr /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/boxtypes/ > /dev/null 2>&1
	rm -fr /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/menu > /dev/null 2>&1
	rm -fr /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts > /dev/null 2>&1
	rm -fr /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/main.cfg > /dev/null 2>&1
	cp /usr/lib/enigma2/python/Plugins/Extensions/release.tgz /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/release.tgz
	cd /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox
	tar xzf release.tgz -C /
	rm release.tgz
	rm /usr/lib/enigma2/python/Plugins/Extensions/release.tgz
	date > /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.lastupdate.log
echo
echo
echo "please reboot enigma now"
echo
	wget -q -O /tmp/.message.txt "http://127.0.0.1/api/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
echo
else
	echo "sorry there is a problem"
fi
exit 0 
