from os import listdir
from os import path as os_path
from os import system

opkgDestinations = ['/']
opkgStatusPath = ''


def findMountPoint(path):
	"""Example: findMountPoint("/media/hdd/some/file") returns "/media/hdd\""""
	path = os_path.abspath(path)
	while not os_path.ismount(path):
		path = os_path.dirname(path)
	return path


def opkgExtraDestinations():
	global opkgDestinations
	return ''.join([" --add-dest %s:%s" % (i, i) for i in opkgDestinations])


def opkgAddDestination(mountpoint):
	global opkgDestinations
	if mountpoint not in opkgDestinations:
		opkgDestinations.append(mountpoint)
		print("[Ipkg] Added to OPKG destinations:", mountpoint)


mounts = listdir('/media')
for mount in mounts:
	mount = os_path.join('/media', mount)
	if mount and not mount.startswith('/media/net'):
		if opkgStatusPath == '':
			# recent opkg versions
			opkgStatusPath = 'var/lib/opkg/status'
			if not os_path.exists(os_path.join('/', opkgStatusPath)):
				# older opkg versions
				opkgStatusPath = 'usr/lib/opkg/status'
		if os_path.exists(os_path.join(mount, opkgStatusPath)):
			opkgAddDestination(mount)

system('opkg ' + opkgExtraDestinations() + ' upgrade 2>&1 | tee /home/root/ipkgupgrade.log && reboot')
