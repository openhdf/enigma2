#!/bin/sh

echo "download licher 19 picons"
mkdir /usr/share/enigma2/picon/
echo
	wget http://addons.hdfreaks.cc/picons/Astra_19_2_HD/picon.tgz -qO /usr/share/enigma2/picon/picon.tgz
		if [ -f /usr/share/enigma2/picon/picon.tgz ]; then 
		cd /usr/share/enigma2/picon/
		echo "extract picons ..."
		tar xzf picon.tgz
		echo
		echo "done ..."
		rm picon.tgz
	echo
	echo
	echo "Picons installed ... please zap now ^^"
	echo
	echo
	else
		echo "sorry there is a problem"
	fi

exit 0 
