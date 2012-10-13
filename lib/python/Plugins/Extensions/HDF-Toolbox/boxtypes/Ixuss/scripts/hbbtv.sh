#!/bin/sh

cd /tmp

if [ -f /etc/enigma2/bookmarks.cfg ]; then 
	echo
	echo "hbbtv bookmarks found"
	cd /etc/enigma2
	echo "make backup"
	mv /etc/enigma2/bookmarks.cfg /etc/enigma2/bookmarks.cfg.ori
	wget http://addons.hdfreaks.cc/et9000/hbbtv/bookmarks.cfg
	echo "Update Done ... "
else
	echo
	echo "no hbbtv plugin found"
	echo
	echo
fi

if [ -f /etc/enigma2/bookmarks_private.cfg ]; then 
	echo
	echo "hbbtv bookmarks_private.cfg found"
	cd /etc/enigma2
	echo "make backup"
	mv /etc/enigma2/bookmarks_private.cfg /etc/enigma2/bookmarks_private.cfg.ori
	wget http://addons.hdfreaks.cc/et9000/hbbtv/bookmarks_private.cfg
	echo "Update Done ... "
else
	echo
	echo "no hbbtv plugin found"
	echo
	echo
fi

#if [ -f /usr/lib/enigma2/python/Plugins/SystemPlugins/WebBrowser/plugin.py ]; then 
#	echo
#	echo "hbbtv plugin found"
#	cd /usr/lib/enigma2/python/Plugins/SystemPlugins/WebBrowser
#	echo "make backup & install icewaere plugin"
#	mv /usr/lib/enigma2/python/Plugins/SystemPlugins/WebBrowser/plugin.py /usr/lib/enigma2/python/Plugins/SystemPlugins/WebBrowser/plugin.py.ori
#	wget http://addons.hdfreaks.cc/et9000/hbbtv/plugin.py
#	echo "Update Done ... Please restart Enigma now"
#	echo
#	echo
#else
#	echo
#	echo "no hbbtv plugin found"
#	echo
#	echo
#fi

exit 0 
