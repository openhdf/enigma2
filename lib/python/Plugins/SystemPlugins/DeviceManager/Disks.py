
import os
import re
from Tools.Directories import fileExists
from Components.SystemInfo import BoxInfo

BLACKLIST = [BoxInfo.getItem("BootDevice")]

class Disks:
	ptypes = {'0': 'Empty',
		'24': 'NEC DOS',
		'81': 'Minix / old Lin',
		'bf': 'Solaris',
		'1': 'FAT12',
		'39': 'Plan 9',
		'82': 'Linux swap / Solaris',
		'c1': 'DRDOS/sec (FAT)',
		'2': 'XENIX root',
		'3c': 'PartitionMagic',
		'83': 'Linux',
		'c4': 'DRDOS/sec (FAT)',
		'3': 'XENIX usr',
		'40': 'Venix 80286',
		'84': 'OS/2 hidden C:',
		'c6': 'DRDOS/sec (FAT)',
		'4': 'FAT16 <32M',
		'41': 'PPC PReP Boot',
		'85': 'Linux extended',
		'c7': 'Syrinx',
		'5': 'Extended',
		'42': 'SFS',
		'86': 'NTFS volume set',
		'da': 'Non-FS data',
		'6': 'FAT16',
		'4d': 'QNX4.x',
		'87': 'NTFS volume set',
		'db': 'CP/M / CTOS',
		'7': 'HPFS/NTFS/exFAT',
		'4e': 'QNX4.x 2nd part',
		'88': 'Linux plaintext',
		'de': 'Dell Utility',
		'8': 'AIX',
		'4f': 'QNX4.x 3rd part',
		'8e': 'Linux LVM',
		'df': 'BootIt',
		'9': 'AIX bootable',
		'50': 'OnTrack DM',
		'93': 'Amoeba',
		'e1': 'DOS access',
		'a': 'OS/2 Boot Manager',
		'51': 'OnTrack DM6 Aux',
		'94': 'Amoeba BBT',
		'e3': 'DOS R/O',
		'b': 'W95 FAT32',
		'52': 'CP/M',
		'9f': 'BSD/OS',
		'e4': 'SpeedStor',
		'c': 'W95 FAT32 (LBA)',
		'53': 'OnTrack DM6 Aux',
		'a0': 'IBM Thinkpad hi',
		'eb': 'BeOS fs',
		'e': 'W95 FAT16 (LBA)',
		'54': 'OnTrackDM6',
		'a5': 'FreeBSD',
		'ee': 'GPT',
		'f': "W95 Ext'd (LBA)",
		'55': 'EZ-Drive',
		'a6': 'OpenBSD',
		'ef': 'EFI',
		'10': 'OPUS',
		'56': 'Golden Bow',
		'a7': 'NeXTSTEP',
		'f0': 'Linux/PA-RISC',
		'11': 'Hidden FAT12',
		'5c': 'Priam Edisk',
		'a8': 'Darwin UFS',
		'f1': 'SpeedStor',
		'12': 'Compaq diagnostic',
		'61': 'SpeedStor',
		'a9': 'NetBSD',
		'f4': 'SpeedStor',
		'14': 'Hidden FAT16',
		'63': 'GNU HURD',
		'ab': 'Darwin boot',
		'f2': 'DOS secondary',
		'16': 'Hidden FAT16',
		'64': 'Novell Netware',
		'af': 'HFS / HFS+',
		'fb': 'VMware VMFS',
		'17': 'Hidden HPFS/NTFS',
		'65': 'Novell Netware',
		'b7': 'BSDI fs',
		'fc': 'VMware VMKCORE',
		'18': 'AST SmartSleep',
		'70': 'DiskSecure Mult',
		'b8': 'BSDI swap',
		'fd': 'Linux raid auto',
		'1b': 'Hidden W95 FAT32',
		'75': 'PC/IX',
		'bb': 'Boot Wizard hidden',
		'fe': 'LANstep',
		'1c': 'Hidden W95 FAT32',
		'80': 'Old Minix',
		'be': 'Solaris boot',
		'ff': 'BBT',
		'1e': 'Hidden W95 FAT16'}

	def __init__(self):
		self.disks = []
		self.readDisks()
		self.readPartitions()

	def readDisks(self):
		partitions = open("/proc/partitions")
		for part in partitions:
			res = re.sub("\\s+", " ", part).strip().split(" ")
			if res and len(res) == 4:
				if (len(res[3]) == 3 and (res[3][:2] == "sd" or res[3][:3] == "hdb")) or (len(res[3]) == 7 and res[3][:7] not in BLACKLIST):
					self.disks.append([res[3],
						int(res[2]) * 1024,
						self.isRemovable(res[3]),
						self.getModel(res[3]),
						self.getVendor(res[3]),
						[],
						self.isRotational(res[3]),
						self.isInternal(res[3])])

	def readPartitions(self):
		partitions = open("/proc/partitions")
		for part in partitions:
			res = re.sub("\\s+", " ", part).strip().split(" ")
			if res and len(res) == 4:
				if (len(res[3]) > 3 and (res[3][:2] == "sd" or res[3][:3] == "hdb")) or (len(res[3]) > 7 and res[3][:7] not in BLACKLIST):
					for i in self.disks:
						if i[0] == res[3][:3] or i[0] == res[3][:7]:
							i[5].append([res[3],
								int(res[2]) * 1024,
								self.getTypeName(res[3]),
								self.getType(res[3])])
							break

	def isRemovable(self, device):
		removable = False
		try:
			data = open('/sys/block/%s/removable' % device, 'r').read().strip()
			removable = int(data)
		except:
			pass
		return removable

	def isRotational(self, device):
		try:
			data = open("/sys/block/%s/queue/rotational" % device, "r").read().strip()
			rotational = int(data)
		except:
			rotational = True
		return rotational

	def isInternal(self, device):
		internal = False
		try:
			phys_path = os.path.realpath(self.sysfsPath('device', device))
			internal = "pci" in phys_path or "ahci" in phys_path or "sata" in phys_path
		except:
			pass
		return internal

	def sysfsPath(self, filename, device):
		return os.path.join('/sys/block/', device, filename)

	def getTypeName(self, device):
		if len(device) > 7:
			dev = device[:7]
			n = device[8:]
		else:
			dev = device[:3]
			n = device[3:]
		cmd = '/usr/sbin/sfdisk --part-type /dev/%s %s' % (dev, n)
		fdisk = os.popen(cmd, 'r')
		res = fdisk.read().strip()
		fdisk.close()
		if res in self.ptypes.keys():
			return self.ptypes[res]
		return res

	def getType(self, device):
		if len(device) > 7:
			dev = device[:7]
			n = device[8:]
		else:
			dev = device[:3]
			n = device[3:]
		cmd = '/usr/sbin/sfdisk --part-type /dev/%s %s' % (dev, n) # use --part-type instead -c
		fdisk = os.popen(cmd, 'r')
		res = fdisk.read().strip()
		fdisk.close()
		return res

	def getModel(self, device):
		try:
			model = open("/sys/block/%s/device/model" % device, "r").read().strip()
			return str(model).replace('\n', '')
		except:
			try:
				model = open("/sys/block/%s/device/name" % device, "r").read().strip()
				return str(model).replace('\n', '')
			except:
				try:
					model = open("/sys/block/%s+p/device/name" % device, "r").read().strip()
					return str(model).replace('\n', '')
				except:
					pass
		return ""

	def getVendor(self, device):
		try:
			vendor = open("/sys/block/%s/device/vendor" % device, "r").read().strip()
			return str(vendor).replace('\n', '')
		except:
			return ""

	def isMounted(self, device):
		mounts = open("/proc/mounts")
		for mount in mounts:
			res = mount.split(" ")
			if res and len(res) > 1:
				if "mmcblk" in device:
					if (res[0] == '/dev/%sp1' % device) or (res[0] == '/dev/%sp2' % device) or (res[0] == '/dev/%sp3' % device) or (res[0] == '/dev/%sp4' % device):
						mounts.close()
						return True
				elif res[0][:8] == '/dev/%s' % device:
					mounts.close()
					return True
		mounts.close()
		return False

	def isMountedP(self, device, partition):
		mounts = open("/proc/mounts")
		for mount in mounts:
			res = mount.split(" ")
			if res and len(res) > 1:
				if res[0] == '/dev/%s%s' % (device, partition):
					mounts.close()
					return True
		mounts.close()
		return False

	def getMountedP(self, device, partition):
		mounts = open("/proc/mounts")
		for mount in mounts:
			res = mount.split(" ")
			if res and len(res) > 1:
				if res[0] == "/dev/%s%d" % (device, partition):
					mounts.close()
					return res[1]
		mounts.close()
		return None

	def umount(self, device):
		mounts = open("/proc/mounts", 'r')
		line = mounts.readlines()
		mounts.close()
		for mnt in line:
			res = mnt.strip().split()
			if res and len(res) > 1:
				if "mmcblk" in device:
					if (res[0] == '/dev/%sp1' % device) or (res[0] == '/dev/%sp2' % device) or (res[0] == '/dev/%sp3' % device) or (res[0] == '/dev/%sp4' % device):
						print("[DeviceManager] umount %s" % res[0])
						if os.system("umount -f %s && sleep 2" % res[0]) != 0:
							return False
				elif res[0][:8] == "/dev/%s" % device:
					print("[DeviceManager] umount %s" % res[0])
					if os.system("umount -f %s && sleep 2" % res[0]) != 0:
						return False
		mounts = open("/proc/mounts", 'r')
		line = mounts.readlines()
		mounts.close()
		for mnt in line:
			res = mnt.strip().split()
			if res and len(res) > 1:
				if "mmcblk" in device:
					if (res[0] == '/dev/%sp1' % device) or (res[0] == '/dev/%sp2' % device) or (res[0] == '/dev/%sp3' % device) or (res[0] == '/dev/%sp4' % device):
						print("[DeviceManager] umount %s" % res[0])
						if os.system("umount -f %s && sleep 2" % res[0]) != 0:
							return False
				elif res[0][:8] == "/dev/%s" % device:
					print("[DeviceManager] umount %s" % res[0])
					if os.system("umount -f %s && sleep 2" % res[3]) != 0:
						return False
		return True

	def umountP(self, device, partition):
		if os.system("umount -f /dev/%s%d && sleep 2" % (device, partition)) != 0:
			return False
		return True

	def mountP(self, device, partition, path):
		if os.system("mount /dev/%s%d %s" % (device, partition, path)) != 0:
			return False
		return True

	def mount(self, fdevice, path):
		if os.system("mount /dev/%s %s" % (fdevice, path)) != 0:
			return False
		return True

	def fdisk(self, device, size, type, fstype=0):
		if self.isMounted(device):
			print("[DeviceManager] device is mounted... umount")
			if not self.umount(device):
				print("[DeviceManager] umount failed!")
				return -1

		if fstype == 0 or fstype == 1 or fstype == 2:
			ptype = "83"
		elif fstype == 3 or fstype == 4:
			ptype = "7"
		elif fstype == 5:
			ptype = "b"
		if type == 0:
			psize = size // 1048576
			if psize > 128000:
				print("[DeviceManager] Detected >128GB disk, using 4k alignment")
				flow = "8,,%s\n0,0\n0,0\n0,0\nwrite\n" % ptype
			else:
				flow = ",,%s\nwrite\n" % ptype
		elif type == 1:
			psize = size // 1048576 // 2
			flow = ",%dM,%s\n,,%s\nwrite\n" % (psize, ptype, ptype)
		elif type == 2:
			psize = size // 1048576 // 4 * 3
			flow = ",%dM,%s\n,,%s\nwrite\n" % (psize, ptype, ptype)
		elif type == 3:
			psize = size // 1048576 // 3
			flow = ",%dM,%s\n,%dM,%s\n,,%s\nwrite\n" % (psize,
				ptype,
				psize,
				ptype,
				ptype)
		elif type == 4:
			psize = size // 1048576 // 4
			flow = ",%dM,%s\n,%dM,%s\n,%dM,%s\n,,%s\nwrite\n" % (psize,
				ptype,
				psize,
				ptype,
				psize,
				ptype,
				ptype)

		cmd = '%s --no-reread -uS /dev/%s' % ('/usr/sbin/sfdisk', device)
		sfdisk = os.popen(cmd, 'w')
		sfdisk.write(flow)
		ret = sfdisk.close()
		print('[DeviceManager]', ret)
		if ret:
			return -2
		os.system("/sbin/mdev -s")
		return 0

	def chkfs(self, device, partition, fstype=0):
		fdevice = '%s%d' % (device, partition)
		print('[DeviceManager] checking device %s' % fdevice)
		if self.isMountedP(device, partition):
			oldmp = self.getMountedP(device, partition)
			print('[DeviceManager] partition is mounted... umount')
			if not self.umountP(device, partition):
				print('[DeviceManager] umount failed!')
				return -1
		else:
			oldmp = ''
		if self.isMountedP(device, partition):
			return -1
		if fstype == 0 or fstype == 1:
			ret = os.system('e2fsck -C 0 -f -p /dev/%s' % fdevice)
		elif fstype == 2:
			tools = "ntfsfix"
			data = os.popen("blkid").readlines()
			for line in data:
				if fdevice in line and 'exfat' in line:
					tools = "exfatfsck"
			ret = os.system('%s /dev/%s' % (tools, fdevice))
		elif fstype == 3:
			ret = os.system('dosfsck -a /dev/%s' % fdevice)
		if len(oldmp) > 0:
			self.mount(fdevice, oldmp)
		if ret == 0:
			return 0
		return -2

	def mkfs(self, device, partition, fstype=0):
		dev = "%s%d" % (device, partition)
		size = 0
		partitions = open("/proc/partitions")
		for part in partitions:
			res = re.sub("\s+", " ", part).strip().split(" ")
			if res and len(res) == 4:
				if res[3] == dev:
					size = int(res[2])
					break

		if size == 0:
			return -1

		if self.isMountedP(device, partition):
			oldmp = self.getMountedP(device, partition)
			print("[DeviceManager] partition is mounted... umount")
			if not self.umountP(device, partition):
				print("[DeviceManager] umount failed!")
				return -2
		else:
			oldmp = ""
		psize = size // 1024
		if fstype == 0:
			cmd = "mkfs.ext4 -F "
			if psize > 20000:
				try:
					version = open('/proc/version', 'r').read().split(' ', 4)[2].split('.', 2)[:2]
					if version[0] > 3 and version[1] >= 2:
						cmd += '-O bigalloc -C 262144 '
				except:
					pass
			cmd += '-m0 -O dir_index /dev/' + dev
		elif fstype == 1:
			cmd = "mkfs.ext3 -F "
			if psize > 250000:
				cmd += "-T largefile -O sparse_super -N 262144 "
			elif psize > 16384:
				cmd += "-T largefile -O sparse_super "
			elif psize > 2048:
				cmd += "-T largefile -N %s " % str(psize * 32)
			cmd += "-m0 -O dir_index /dev/" + dev
			os.system("opkg update && opkg install kernel-module-ext3")
		elif fstype == 2:
			cmd = 'mkfs.ext2 -F '
			if psize > 2048:
					cmd += '-T largefile '
			cmd += '-m0 /dev/' + dev
			os.system("opkg update && opkg install kernel-module-ext2")
		elif fstype == 3:
			cmd = "mkfs.ntfs -f /dev/" + dev
		elif fstype == 4:
			cmd = "mkfs.exfat /dev/" + dev
		elif fstype == 5:
			if psize > 4194304:
				cmd = 'mkfs.vfat -I -S4096 -F32 /dev/' + dev
			else:
				cmd = 'mkfs.vfat -I -F32 /dev/' + dev
		else:
			if len(oldmp) > 0:
				self.mount(dev, oldmp)
			return -3
		ret = os.system(cmd)

		if len(oldmp) > 0:
			self.mount(dev, oldmp)

		if ret == 0:
			return 0
		return -3
