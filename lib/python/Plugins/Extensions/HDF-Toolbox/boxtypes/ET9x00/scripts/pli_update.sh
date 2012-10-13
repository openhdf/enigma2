#!/bin/sh

cd /tmp
echo "Download and install update"

if [ `cat /proc/stb/info/chipset` = bcm7405 ]; then 
	echo
	echo "Boxtype et9000"
	echo
	echo "starting okgp update & upgrade"
    opkg update  > /dev/null 2>&1
	opkg upgrade
	echo
	echo "Update Done ... Please reboot your Box now!"
	echo
	wget -q -O /tmp/.message.txt "http://127.0.0.1/web/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
	wget -q -O /tmp/.message.txt "http://127.0.0.1/api/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
fi
	
if [ `cat /proc/stb/info/chipset` = 7335 ]; then 
	echo
	echo "Boxtype vuduo"
	echo
	echo "starting okgp update & upgrade"
    opkg update  > /dev/null 2>&1
	opkg upgrade
	echo
	echo "Update Done ... Please reboot your Box now!"
	wget -q -O /tmp/.message.txt "http://127.0.0.1/web/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
	wget -q -O /tmp/.message.txt "http://127.0.0.1/api/message?text=Update%20done%20...%20please%20reboot%20your%20STB%20now%20...&type=2" &  > /dev/null 2>&1
fi

exit 0 
