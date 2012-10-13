#!/bin/sh

echo
echo "delete timestamp in /etc"
rm -f /etc/timestamp
echo
echo "Timestamp removed ... Please reboot your Box now!"
echo

exit 0   
