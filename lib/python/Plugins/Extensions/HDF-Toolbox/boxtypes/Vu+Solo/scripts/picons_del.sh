#!/bin/sh

echo "remove all picon from flash"
rm -f /usr/share/enigma2/picon/coolpico/*.* > /dev/null 2>&1
rm -f /usr/share/enigma2/picon/*.* > /dev/null 2>&1
rmdir /usr/share/enigma2/picon > /dev/null 2>&1
echo
echo "Picon removed"
echo

exit 0 
