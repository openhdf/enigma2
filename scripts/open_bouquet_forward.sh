#!/bin/sh
# script to open next boquet
wget -qO /tmp/.message.txt 'http://127.0.0.1/web/remotecontrol?command=103' &  > /dev/null 2>&1
sleep 1
wget -qO /tmp/.message.txt 'http://127.0.0.1/web/remotecontrol?command=402' &  > /dev/null 2>&1
