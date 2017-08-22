#!/bin/sh
# script to open last boquet
wget -qO /tmp/.message.txt 'http://127.0.0.1/web/remotecontrol?command=103' &  > /dev/null 2>&1
sleep 1
wget -qO /tmp/.message.txt 'http://127.0.0.1/web/remotecontrol?command=403' &  > /dev/null 2>&1
