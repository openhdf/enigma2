#!/bin/sh

echo "opkg update feed"
opkg update > /dev/null
echo
echo "install new xmltvimport-rytec & xmltvimport"
opkg upgrade enigma2-plugin-extensions-xmltvimport-rytec enigma2-plugin-extensions-xmltvimport
echo
echo "done"
echo
exit 0 
