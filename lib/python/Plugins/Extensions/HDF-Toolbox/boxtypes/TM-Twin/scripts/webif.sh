#!/bin/sh

cd /tmp
echo "Download and install update"

if [ `cat /proc/stb/info/chipset` = bcm7405 ]; then 
	echo
	echo "Boxtype et9000"
	echo
	wget http://addons.hdfreaks.cc/et9000/webif.tar.gz
		if [ -f /tmp/webif.tar.gz ]; then 
		echo
		echo "extract files"
		cd /
		tar xzvf /tmp/webif.tar.gz > /dev/null 2>&1
		rm -f /tmp/webif.tar.gz > /dev/null 2>&1
		echo
		echo "Update Done ... Please reboot your Box now!"
		echo
fi
fi

if [ `cat /proc/stb/info/chipset` = 7335 ]; then 
	echo
	echo "Boxtype vuduo"	
	echo
	wget http://addons.hdfreaks.cc/vuduo/webif.tar.gz
		if [ -f /tmp/webif.tar.gz ]; then 
		echo
		echo "extract files"
		cd /
		tar xzvf /tmp/webif.tar.gz > /dev/null 2>&1
		rm -f /tmp/webif.tar.gz > /dev/null 2>&1
		echo
		echo "Update Done ... Please reboot your Box now!"
		echo
fi
fi

exit 0 
