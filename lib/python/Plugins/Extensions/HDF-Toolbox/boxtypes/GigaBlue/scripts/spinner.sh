#!/bin/sh

cd /tmp
echo "Download and install update"
	echo
	echo "Boxtype GigaBlue"
	echo
	echo "starting okgp update & upgrade"
 	opkg update > /dev/null 2>&1
	opkg upgrade
	echo
	wget http://addons.hdfreaks.cc/feeds/enigma2-plugins-update-HDFreaks_SpinnerupdateGigaBlue.tar.gz
	echo
	echo "extract files"
	rm -f /usr/share/enigma2/skin_default/spinner/wait*.*
	cd /
	tar xzvf /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateGigaBlue.tar.gz > /dev/null 2>&1
	rm -f /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateGigaBlue.tar.gz > /dev/null 2>&1
	echo
	echo "Update Done ... Please reboot your Box now!"
	echo
	wget -q -O /tmp/.message.txt "http://127.0.0.1/api/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
exit 0 
