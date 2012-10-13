#!/bin/sh

#set temp output file
touch /tmp/hdf.txt

if [ -f /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate ]; then
	if [ -f /etc/enigma2/.transponderupdate ]; then
			echo "update time & date from multiplex"
			/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate --set --force --timeout 60 &
			echo DATE > /proc/vfd
			if [ $? == 0 ]; then
			echo "update done ..."
			else
			echo "update failed ... try again"
			/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate --set --force --quiet --timeout 15 &
			echo date > /proc/vfd
			echo "and the last try"
			/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/dvbdate --set --force --quiet --timeout 15 &
			echo date > /proc/vfd
			fi
		else
		echo "auto timeupdate from multiplex deactivated"
	fi
else
	echo "no binary dvbdate found"
fi
