#!/bin/sh

cd /tmp
echo "Download and install update"

if [ `cat /proc/stb/info/chipset` = bcm7405 ]; then 
	echo
	echo "Boxtype et9x00/et6x00"
	echo
	echo "starting okgp update & upgrade"
    	opkg update > /dev/null 2>&1
		opkg upgrade
	echo
	cd /tmp
	echo
	wget http://addons.hdfreaks.cc/feeds/enigma2-plugins-update-HDFreaks_SpinnerupdateET9x00.tar.gz
	echo
	if [ -f /etc/opkg/et9x00-feed.conf ]; then
		echo "New et9x00 Image found"
	if [ -f /etc/opkg/et9000-feed.conf ]; then
	echo "Old et9000 Image found ... download HdmiCec.py from PLi Git"
	wget 'http://openpli.git.sourceforge.net/git/gitweb.cgi?p=openpli/enigma2;a=blob_plain;f=lib/python/Components/HdmiCec.py;hb=HEAD' -O /usr/lib/enigma2/python/Components/HdmiCec.py
	fi
	fi
	echo
	echo "extract files"
	cd /
	tar xzvf /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateET9x00.tar.gz > /dev/null 2>&1
	rm -f /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateET9x00.tar.gz > /dev/null 2>&1
	echo
	echo "Update Done ... Please reboot your Box now!"
	echo
	wget -q -O /tmp/.message.txt "http://127.0.0.1/api/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
	#wget -q -O /tmp/.message.txt "http://127.0.0.1/web/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
fi
	
if [ `cat /proc/stb/info/chipset` = 7335 ]; then 
	echo
	echo "Boxtype vuduo"
	echo
	echo "starting okgp update & upgrade"
 	opkg update > /dev/null 2>&1
	opkg upgrade
	echo
	wget http://addons.hdfreaks.cc/feeds/enigma2-plugins-update-HDFreaks_SpinnerupdateVuduo.tar.gz
	echo
	echo "extract files"
	cd /
	tar xzvf /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateVuduo.tar.gz > /dev/null 2>&1
	rm -f /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateVuduo.tar.gz > /dev/null 2>&1
	echo
	echo "Update Done ... Please reboot your Box now!"	
	wget -q -O /tmp/.message.txt "http://127.0.0.1/api/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
	#wget -q -O /tmp/.message.txt "http://127.0.0.1/web/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
fi

if [ `cat /proc/stb/info/chipset` = 7325 ]; then 
	echo
	echo "Boxtype vusolo"
	echo
	echo "starting okgp update & upgrade"
 	opkg update > /dev/null 2>&1
	opkg upgrade
	echo
	wget http://addons.hdfreaks.cc/feeds/enigma2-plugins-update-HDFreaks_SpinnerupdateVUSolo.tar.gz
	echo
	echo "extract files"
	cd /
	tar xzvf /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateVUSolo.tar.gz > /dev/null 2>&1
	rm -f /tmp/enigma2-plugins-update-HDFreaks_SpinnerupdateVUSolo.tar.gz > /dev/null 2>&1
	echo
	echo "Update Done ... Please reboot your Box now!"
	wget -q -O /tmp/.message.txt "http://127.0.0.1/api/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
	#wget -q -O /tmp/.message.txt "http://127.0.0.1/web/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
fi

exit 0 
