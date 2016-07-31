#
# EcmCryptoInfo Converter by mcbain // v0.1 // 20111109
#
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Poll import Poll

import os

ECM_INFO = '/tmp/ecm.info'

old_ecm_mtime = None
data = None

class EcmCryptoInfo(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		
		self.active = False
		self.visible = config.usage.show_cryptoinfo.value
		self.textvalue = ''
		self.poll_interval = 2*1000
		if self.visible:
			self.poll_enabled = True
		else:
			self.poll_enabled = False

	@cached
	def getText(self):
		if not self.visible:
			return ''
		ecmdata = self.getEcmData()
		return ecmdata
	text = property(getText)

	def getEcmData(self):
		global old_ecm_mtime
		global data
		try:
			ecm_mtime = os.stat(ECM_INFO).st_mtime
		except:
			ecm_mtime = None
		if ecm_mtime != old_ecm_mtime:
			old_ecm_mtime = ecm_mtime
			data = self.getEcmInfo()
		return data

	def getEcmInfo(self):
		try:
			ecm = open(ECM_INFO, 'rb').readlines()
			ecminfo = {}
			for line in ecm:
				d = line.split(':', 1)
				if len(d) > 1:
					ecminfo[d[0].strip()] = d[1].strip()
			# ecminfo is dictionary
			if (ecminfo == ''):
				return 'No info from emu or FTA'

			using = ecminfo.get('using', '')
			if using:
				# CCcam
				if using == 'fta':
					return 'Free to Air'

				ecmInfoString=''
				casys=''
				state='Source: '
				caid = ecminfo.get('caid', '')
				address = ecminfo.get('address', '')
				hops = ecminfo.get('hops', '')
				ecmtime = ecminfo.get('ecm time', '')

				if caid:
					if caid.__contains__('x'):
						idx = caid.index('x')
						caid = caid[idx+1:]
						if len(caid) == 3:
							caid = '0%s' % caid
						caid = caid.upper()
					casys = 'Caid: '+caid
				if address:
					retaddress = '%s %s' % (_(' Source:'), address)
					if address == ('/dev/sci0'):
						state = (' Source: Lower slot')
					if address == ('/dev/sci1'):
						state = (' Source: Upper slot')
					if address != ('/dev/sci0') and address != ('/dev/sci1'):
						state = retaddress
					if len(state) > 28:
						state = ('%s...') % state[:25]
				if hops:
					hops = '%s %s' % (_(' Hops:'), hops)
				if ecmtime:
					ecmtime = '%s %ss' % (_(' Time:'), ecmtime)
		
				if casys != '':
					ecmInfoString = '%s ' % casys
				if state != 'Source: ':
					ecmInfoString = '%s%s ' % (ecmInfoString, state)
				if state == 'Source: ':
					ecmInfoString += state
					ecmInfoString = '%s%s ' % (ecmInfoString, using)
				if hops != '' and hops != ' Hops: 0':
					ecmInfoString = '%s%s ' % (ecmInfoString, hops)
				if ecmtime != '':
					ecmInfoString = '%s%s ' % (ecmInfoString, ecmtime)
				self.textvalue = ecmInfoString
			else:
				return 'No info from emu or unknown emu'
		except:
			self.textvalue = ''

		return self.textvalue
