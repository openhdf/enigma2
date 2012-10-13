#!/bin/sh

cd /tmp
echo "Download and install Oscam_yModV"
wget http://addons.hdfreaks.cc/et9000/oscam_emu/Oscam_yModV.tgz
echo
echo "extract files to:"
cd /
tar xzvf /tmp/Oscam_yModV.tgz
rm -f /tmp/Oscam_yModV.tgz
echo
echo "symlink oscam.keys to SoftCam.key"
rm -f /etc/tuxbox/config/oscam_emu/oscam.keys
ln -s /usr/keys/SoftCam.Key /etc/tuxbox/config/oscam_emu/oscam.keys
echo
echo "Update Done ... Please start Oscam_yModV from Softcam Manager!"
echo
exit 0   
