#!/bin/sh

if [ -f /etc/.djmount ]; then 
	echo
	/etc/init.d/djmount stop
	chmod 644 /etc/init.d/djmount
	rm -f /etc/.djmount
	echo
	echo "djmount DLNA Client autostart is now OFF"
	echo
	echo
else
	echo
	chmod 755 /etc/init.d/djmount
	touch /etc/.djmount
	/etc/init.d/djmount start
	echo
	echo "djmount DLNA Client autostart is now ON"
	echo "You can find the UPNP/DLNA Server inside /media/upnp/"
	echo
	echo
fi
exit 0 
