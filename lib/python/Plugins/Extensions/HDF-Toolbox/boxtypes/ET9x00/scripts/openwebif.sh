#!/bin/sh
echo "Download new version"
IP=hdfreaks.cc
ping -c 1 $IP > /dev/null 2>&1
if [ $? == 0 ]
	then
		wget http://addons.hdfreaks.cc/openwebif/master.tgz -O /usr/lib/enigma2/python/Plugins/Extensions/master.tgz
		echo "download complete"
	else
  		echo "update failed"
fi;

if [ -f /usr/lib/enigma2/python/Plugins/Extensions/master.tgz ]; then 
	rm -fr /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/ > /dev/null 2>&1
	mkdir /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif > /dev/null 2>&1
	mv /usr/lib/enigma2/python/Plugins/Extensions/master.tgz /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/master.tgz > /dev/null 2>&1
	cd /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif
	tar xzf master.tgz > /dev/null 2>&1
	cd E2OpenPlugins-e2openplugin-OpenWebif-*
	cd plugin
	mv -f * /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/
	cd /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/
	rm -fr master.tgz
	rm -fr E2OpenPlugins-e2openplugin*
	echo
	echo "please wait ... precompile templates"
	echo
	echo "--> controllers/views"
	/usr/bin/cheetah-compile /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/controllers/views/*.tmpl > /dev/null 2>&1
	echo "--> controllers/views/web"
	/usr/bin/cheetah-compile /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/controllers/views/web/*.tmpl > /dev/null 2>&1
	echo "--> controllers/views/ajax"
	/usr/bin/cheetah-compile /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/controllers/views/ajax/*.tmpl > /dev/null 2>&1
	echo "--> controllers/views/mobile"
	/usr/bin/cheetah-compile /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/controllers/views/mobile/*.tmpl > /dev/null 2>&1
	echo
	echo "done ... please reboot enigma now"
	echo
		else
		echo "sorry there is a problem"
fi

exit 0 
