#!/bin/sh
##Backup Script Gigablue by HDFreaks.cc

TARGET=`cat /proc/mounts | grep sd | cut -d" " -f2`
PPATH="/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts"

if [ -z $TARGET ]
	then
	echo "no backup medium found"
	exit
fi

##Gigablue SOLO Full Backup
if [ -f /etc/.gigablue_solo ]; then  
echo "Gigablue Solo found"
DIR="Full-Backup-Solo"
echo
mkdir $TARGET/$DIR > /dev/null 2>&1
cd $TARGET/$DIR
rm -f $TARGET/$DIR/burn.bat > /dev/null 2>&1
touch $TARGET/$DIR/burn.bat
echo "flash -noheader usbdisk0:ker_e2.img flash1.user " > burn.bat
echo "setenv -p STARTUP" '"boot -z -elf flash0.kernel: '"'rootfstype=jffs2 bmem=106M@150M root=/dev/mtdblock6 rw '"'"'"  " >> burn.bat
echo "" >> burn.bat
df -h | grep $TARGET
echo
echo "Create Full-Backup to $TARGET ... please wait"
echo
echo "copy rootfs to $TARGET/$DIR/rootfs.img"
if [ -f /dev/mtdblock0 ]; then
	cat /dev/mtdblock0 > $TARGET/$DIR/rootfs.img
	else
	cat /dev/mtd0 > $TARGET/$DIR/rootfs.img
fi
echo "copy kernel image to $TARGET/$DIR/kernel.img"
cp /home/root/.vmlinuxSOLO $TARGET/$DIR/kernel.img
echo "create ker_e2.img $TARGET/$DIR/ker_e2.img"
cat kernel.img rootfs.img > ker_e2.img
rm -f kernel.img
rm -f rootfs.img
echo "HDFreaks "> $TARGET/$DIR/version.txt
date >> $TARGET/$DIR/version.txt
echo
echo "The Image is now ready to flash"
echo "..."
echo "Copy the content from $TARGET/$DIR/"
echo "to a Fat/Fat32 formated USB-Stick."
echo "Plug in the USB-Stick to your Box and turn it on."
echo "The Image will automatically flash to your Box."
echo "Don't stop or break the flashing to your Box!"
fi

##Gigablue SE Full Backup
if [ -f /etc/.gigablue_se ]; then 
echo "Gigablue SE found"
DIR="Full-Backup-SE"
echo
mkdir $TARGET/$DIR > /dev/null 2>&1
cd $TARGET/$DIR
rm -f $TARGET/$DIR/burn.bat > /dev/null 2>&1
touch $TARGET/$DIR/burn.bat
echo "macprog2 AC-DB-EF-11-22-11" > burn.bat
echo "flasherase -all" >> burn.bat
echo "flash -noheader usbdisk0:vmlinux.gz nandflash0.kernel" >> burn.bat
echo "flash -noheader usbdisk0:rootfs_hdf.img nandflash0.avail0" >> burn.bat
echo 'setenv -p STARTUP "boot -z -elf nandflash0.kernel:"' >> burn.bat
echo "boot -z -elf nandflash0.kernel:" >> burn.bat
df -h | grep $TARGET
echo
echo "Create Full-Backup to $TARGET ... please wait"
echo
echo "copy rootfs to $TARGET/$DIR/rootfs_hdf.img"
mkdir /mnt/backup
mount -t jffs2 /dev/mtdblock0 /mnt/backup
ddbrootfs -n -l -e131072 -d/mnt/backup -o$TARGET/$DIR/rootfs_hdf.img
echo "copy kernel image to $TARGET/$DIR/vmlinux"
cp /home/root/.vmlinuxSE.gz $TARGET/$DIR/vmlinux.gz
echo "HDFreaks "> $TARGET/$DIR/version.txt
date >> $TARGET/$DIR/version.txt
umount -f /mnt/backup
echo
echo "The Image is now ready to flash"
echo "..."
echo "Copy the content from $TARGET/$DIR/"
echo "to a Fat/Fat32 formated USB-Stick."
echo "Plug in the USB-Stick to your Box and turn it on."
echo "The Image will automatically flash to your Box."
echo "Don't stop or break the flashing to your Box!"
echo
fi
