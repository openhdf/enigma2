#!/bin/sh

echo "sync time with pool.ntp.org"
echo
ntpdate -u pool.ntp.org
echo
exit 0   
