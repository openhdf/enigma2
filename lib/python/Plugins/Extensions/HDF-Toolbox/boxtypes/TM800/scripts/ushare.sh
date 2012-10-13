#!/bin/sh

if [ -f /etc/.ushare ]; then 
	echo
	/etc/init.d/ushare stop
	chmod 644 /etc/init.d/ushare
	rm -f /etc/.ushare
	echo
	echo "uShare UPnP Server autostart is now OFF"
	echo
	echo
else
	echo
	chmod 755 /etc/init.d/ushare
	touch /etc/.ushare
	/etc/init.d/ushare start
	echo
	echo "uShare UPnP Server autostart is now ON"
	echo
	echo
fi
exit 0 
