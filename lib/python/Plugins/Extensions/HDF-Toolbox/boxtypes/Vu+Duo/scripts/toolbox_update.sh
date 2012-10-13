#!/bin/sh

echo
echo "Autoupdate HDF Toolbox"

if [ -f /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.autoupdate ]; then 
	echo
	rm /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.autoupdate
	echo "... is now OFF"
	echo
	echo
else
	echo
	touch /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.autoupdate
	echo "... is now ON"
	echo
	echo
fi
exit 0 
