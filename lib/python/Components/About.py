from boxbranding import getBoxType, getImageVersion, getMachineBuild
from sys import modules
import socket
import fcntl
import struct
import time
import os
from os import path


def getVersionString():
	return getImageVersion()


def getFlashDateString():
	try:
		tm = time.localtime(os.stat("/etc/version").st_mtime)
		if tm.tm_year >= 2011:
			return time.strftime(_("%d.%m.%Y %H:%M:%S"), tm)
		else:
			return _("unknown")
	except:
		return _("unknown")


def getEnigmaVersionString():
	return getImageVersion()


def getGStreamerVersionString():
	import enigma
	return enigma.getGStreamerVersionString()


def getKernelVersionString():
	try:
		f = open("/proc/version", "r")
		kernelversion = f.read().split(' ', 4)[2].split('-', 2)[0]
		f.close()
		return kernelversion
	except:
		return _("unknown")


def getModelString():
		model = getBoxType()
		return model


def getChipSetString():
	if getMachineBuild() in ('dm7080', 'dm820'):
		return "7435"
	elif getMachineBuild() in ('dm520', 'dm525'):
		return "73625"
	elif getMachineBuild() in ('dm900', 'dm920'):
		return "7252S"
	elif getMachineBuild() in ('hd51', 'sf4008'):
		return "7251S"
	else:
		try:
			f = open('/proc/stb/info/chipset', 'r')
			chipset = f.read()
			f.close()
			return str(chipset.lower().replace('\n', '').replace('bcm', '').replace('brcm', '').replace('sti', ''))
		except IOError:
			return "unavailable"


def getCPUString():
	if getMachineBuild() in ('vuuno4k', 'vuultimo4k', 'vusolo4k', 'hd51', 'hd52', 'sf4008', 'dm900', 'dm920', 'gb7252', 'gbx34k', 'dags7252', 'vs1500', 'h7', '8100s', 'osmio4k', 'osmio4kplus', 'osmini4k'):
		return "Broadcom "
	elif getMachineBuild() in ('dagsmv200', 'gbmv200', 'u41', 'u42', 'u43', 'u45', 'u51', 'u52', 'u53', 'u532', 'u533', 'u54', 'u55', 'u56', 'u57', 'u571', 'u5', 'u5pvr', 'h9', 'i55se', 'h9se', 'h9combose', 'h9combo', 'h10', 'h11', 'cc1', 'sf8008', 'sf8008m', 'sf8008opt', 'sx988', 'hd60', 'hd61', 'pulse4k', 'pulse4kmini', 'i55plus', 'ustym4kpro', 'ustym4kott', 'beyonwizv2', 'viper4k', 'multibox', 'multiboxse', 'hzero', 'h8', 'sfx6008'):
		return "Hisilicon"
	else:
		try:
			system = "unknown"
			file = open('/proc/cpuinfo', 'r')
			lines = file.readlines()
			for x in lines:
				splitted = x.split(': ')
				if len(splitted) > 1:
					splitted[1] = splitted[1].replace('\n', '')
					if splitted[0].startswith("system type"):
						system = splitted[1].split(' ')[0]
					elif splitted[0].startswith("Processor"):
						system = splitted[1].split(' ')[0]
			file.close()
			return system
		except IOError:
			return "unavailable"


def getCPUSpeedString():
	if getMachineBuild() in ('vusolo4k', 'gbx34k'):
		return "1,5 GHz"
	elif getMachineBuild() in ('vuuno4k', 'dm900', 'gb7252', 'dags7252'):
		return "1,7 GHz"
	elif getMachineBuild() in ('dagsmv200', 'gbmv200', 'u51', 'u52', 'u53', 'u532', 'u533', 'u54', 'u55', 'u56', 'u57', 'u571', 'u5', 'u5pvr', 'h9', 'i55se', 'h9se', 'h9combose', 'h9combo', 'h10', 'h11', 'cc1', 'sf8008', 'sf8008m', 'sf8008opt', 'sx988', 'hd60', 'hd61', 'pulse4k', 'pulse4kmini', 'i55plus', 'ustym4kpro', 'ustym4kott', 'beyonwizv2', 'viper4k', 'multibox', 'multiboxse'):
		return "1,6 GHz"
	elif getMachineBuild() in ('sfx6008', 'sfx6018'):
		return "1,2 GHz"
	elif getMachineBuild() in ('u41', 'u42'):
		return "1,0 GHz"
	elif getMachineBuild() in ('formuler1tc', 'formuler1', 'triplex'):
		return "1,3 GHz"
	elif getMachineBuild() in ('hd51', 'hd52', 'sf4008', 'vs1500', 'et1x000', 'h7', '8100s', 'osmio4k', 'osmio4kplus', 'osmini4k'):
		try:
			import binascii
			f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
			clockfrequency = f.read()
			f.close()
			return "%s MHz" % str(round(int(binascii.hexlify(clockfrequency), 16) / 1000000, 1))
		except:
			return "1,7 GHz"
	else:
		try:
			file = open('/proc/cpuinfo', 'r')
			lines = file.readlines()
			for x in lines:
				splitted = x.split(': ')
				if len(splitted) > 1:
					splitted[1] = splitted[1].replace('\n', '')
					if splitted[0].startswith("cpu MHz"):
						mhz = float(splitted[1].split(' ')[0])
						if mhz and mhz >= 1000:
							mhz = "%s GHz" % str(round(mhz / 1000, 1))
						else:
							mhz = "%s MHz" % str(round(mhz, 1))
			file.close()
			return mhz
		except IOError:
			return "unavailable"


def getCpuCoresString():
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n', '')
				if splitted[0].startswith("processor"):
					if getMachineBuild() in ('dagsmv200', 'gbmv200', 'u51', 'u52', 'u53', 'u532', 'u533', 'u54', 'u55', 'u56', 'u57', 'u571', 'vuultimo4k', 'u5', 'u5pvr', 'h9', 'i55se', 'h9se', 'h9combose', 'h9combo', 'h10', 'h11', 'alien5', 'cc1', 'sf8008', 'sf8008m', 'sf8008opt', 'sx988', 'hd60', 'hd61', 'pulse4k', 'pulse4kmini', 'i55plus', 'ustym4kpro', 'ustym4kott', 'beyonwizv2', 'viper4k', 'vuduo4k', 'vuduo4kse', 'multibox', 'multiboxse'):
						cores = 4
					elif getMachineBuild() in ('u41', 'u42', 'u43', 'u45'):
						cores = 1
					elif int(splitted[1]) > 0:
						cores = 2
					else:
						cores = 1
		file.close()
		return cores
	except IOError:
		return "unavailable"


def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', ifname[:15])
	info = fcntl.ioctl(sock.fileno(), addr, iface)
	if addr == 0x8927:
		return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].upper()
	else:
		return socket.inet_ntoa(info[20:24])


def getIfConfig(ifname):
	ifreq = {'ifname': ifname}
	infos = {}
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# offsets defined in /usr/include/linux/sockios.h on linux 2.6
	infos['addr'] = 0x8915 # SIOCGIFADDR
	infos['brdaddr'] = 0x8919 # SIOCGIFBRDADDR
	infos['hwaddr'] = 0x8927 # SIOCSIFHWADDR
	infos['netmask'] = 0x891b # SIOCGIFNETMASK
	try:
		for k, v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass
	sock.close()
	return ifreq


def GetIPsFromNetworkInterfaces():
	import socket
	import fcntl
	import struct
	import array
	import sys
	is_64bits = sys.maxsize > 2**32
	struct_size = 40 if is_64bits else 32
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	max_possible = 8 # initial value
	while True:
		_bytes = max_possible * struct_size
		names = array.array('B')
		for i in range(0, _bytes):
			names.append(0)
		outbytes = struct.unpack('iL', fcntl.ioctl(
			s.fileno(),
			0x8912,  # SIOCGIFCONF
			struct.pack('iL', _bytes, names.buffer_info()[0])
		))[0]
		if outbytes == _bytes:
			max_possible *= 2
		else:
			break
	namestr = names.tostring()
	ifaces = []
	for i in range(0, outbytes, struct_size):
		iface_name = bytes.decode(namestr[i:i + 16]).split('\0', 1)[0].encode('ascii')
		if iface_name != 'lo':
			iface_addr = socket.inet_ntoa(namestr[i + 20:i + 24])
			ifaces.append((iface_name, iface_addr))
	return ifaces


def getIfTransferredData(ifname):
	f = open('/proc/net/dev', 'r')
	for line in f:
		if ifname in line:
			data = line.split('%s:' % ifname)[1].split()
			rx_bytes, tx_bytes = (data[0], data[8])
			f.close()
			return rx_bytes, tx_bytes


def getPythonVersionString():
	try:
		import commands
		status, output = commands.getstatusoutput("python -V")
		return output.split(' ')[1]
	except:
		return _("unknown")


def getBoxUptime():
	try:
		time = ''
		f = open("/proc/uptime", "rb")
		secs = int(f.readline().split('.')[0])
		f.close()
		if secs > 86400:
			days = secs / 86400
			secs = secs % 86400
			time = ngettext("%d day", "%d days", days) % days + " "
		h = secs / 3600
		m = (secs % 3600) / 60
		time += ngettext("%d hour", "%d hours", h) % h + " "
		time += ngettext("%d minute", "%d minutes", m) % m
		return "%s" % time
	except:
		return '-'


# For modules that do "from About import about"
about = modules[__name__]
