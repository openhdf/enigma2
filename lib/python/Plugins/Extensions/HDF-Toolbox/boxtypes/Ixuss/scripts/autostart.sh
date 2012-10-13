#!/bin/sh

#set temp output file
touch /tmp/hdf.txt

#download changelog
cd /tmp
wget -q http://addons.hdfreaks.cc/et9000/changelog -Oet9000_changelog
####

if [ -f /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate ]; then
	if [ -f /etc/enigma2/.transponderupdate ]; then
			echo "update time & date from multiplex"
			/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate --set --force --timeout 60 &
			if [ $? == 0 ]; then
			echo "update done ..."
			echo
			else
			echo "update failed ... try again"
			/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate --set --force --quiet --timeout 15 &
			echo "and the last try"
			echo
			/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate --set --force --quiet --timeout 15 &
			echo
			fi
		else
		echo "auto timeupdate from multiplex deactivated"
	fi
else
	echo "no binary dvbdate found"
fi

