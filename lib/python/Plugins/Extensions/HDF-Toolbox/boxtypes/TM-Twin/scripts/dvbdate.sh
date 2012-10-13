#!/bin/sh

echo
echo "Autoupdate Multiplex Update"

if [ -f /etc/enigma2/.transponderupdate ]; then 
	echo
	rm /etc/enigma2/.transponderupdate
	chmod 755 /etc/init.d/ddtime_e2
	echo "... is now OFF"
	echo
	echo
else
	echo
	touch /etc/enigma2/.transponderupdate
	echo "... is now ON ... try to receive time from channel on every bootup"
	chmod 644 /etc/init.d/ddtime_e2
	echo 
	/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts/autostart.sh
	echo
	echo
fi
exit 0 
