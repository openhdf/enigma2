#!/bin/sh

if [ -f /etc/.browser ]; then 
	echo
	killall browser
	chmod 644 /usr/local/browser/browser
	rm -f /etc/.browser
	echo
	echo "ETXx00 Webbrowser autostart is now OFF"
	echo
	echo
else
	echo
	chmod 755 /usr/local/browser/browser
	touch /etc/.browser
	echo "please wait ... starting browser"
	sleep 2
	cd /usr/local/browser/ 
	./browser -u /usr/local/browser/index.html
	echo
	echo "ETXx00 Webbrowser autostart is now ON"
	echo "You can start HbbTV Apps with Mark button on your rc"
	echo "If not ... please restart Enigma2 GUI"
	echo
	echo
fi
exit 0 
