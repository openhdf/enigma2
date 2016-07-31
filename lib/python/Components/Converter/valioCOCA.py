#######################################################################
#
#    Converter CAID's for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2011
#
#######################################################################




from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached
from Components.config import config
from Poll import Poll



class valioCOCA(Poll, Converter, object):
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.type = type
		self.systemCaids = {
			"06" : "I",
			"01" : "S",
			"18" : "N",
			"05" : "V",
			"0B" : "CO",
			"17" : "B",
			"0D" : "CW",
			"4A" : "DC",
			"55" : "BG",
			"09" : "ND" }
		if config.valiflex.showEinfo.value == "showE":
			self.have2show = True
		else:
			self.have2show = False
		self.poll_interval = 2000
		self.poll_enabled = True

	@cached
	def get_caidlist(self):
		caidlist = {}
		textvalue = " " 
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				caids = info.getInfoObject(iServiceInformation.sCAIDs)
				if caids and self.have2show:
					for caid in caids:
						c = "%x" % int(caid)
						if len(c) == 3:
							c = "0%s" % c
						c = c[:2].upper()
						if self.systemCaids.has_key(c) and not caidlist.has_key(c):
							caidlist[c] = (self.systemCaids.get(c),0)
					ecm_info = self.ecmfile()
					if ecm_info:
						emu_caid = ecm_info.get("caid", "")
						if emu_caid and emu_caid != "0x000":
							c = emu_caid.lstrip("0x")
							if len(c) == 3:
								c = "0%s" % c
							c = c[:2].upper()
							caidlist[c] = (self.systemCaids.get(c),1)
						# caid
						caid = ecm_info.get("caid", "")
						caid = caid.lstrip("0x")
						caid = caid.upper()
						caid = caid.zfill(4)
						# hops
						hops = ecm_info.get("hops", None)
						if hops and hops != "0":
							hops = "(%s)" % hops
						else:
							hops = ""
						# ecm time	
						ecm_time = ecm_info.get("ecm time", None)
						if ecm_time:
							if "msec" in ecm_time:
								ecm_time = "%s -" % ecm_time						
							elif ecm_time != "nan":
								ecm_time = "%ss -" % ecm_time
							else:
								ecm_time = ""
						# address
						address = ecm_info.get("address", "")
						if address:
							if address == "/dev/sci0":
								address = "Slot #1"
							elif address == "/dev/sci1":
								address = "Slot #2"								
						# source	
						using = ecm_info.get("using", "")
						if using:
							if using == "emu":
								textvalue = " - %s %s" % (caid, ecm_time)
							elif using == "CCcam-s2s":
								textvalue = " - %s - %s %s %s" % (caid, ecm_time, hops, self.kurz(address))							
							else:
								textvalue = " - %s - %s %s" % (caid, ecm_time, self.kurz(address))		
						else:
							# mgcamd
							source = ecm_info.get("source", None)
							if source:
								if source == "emu":
									textvalue = " - %s" % (caid)
								else:
									textvalue = " - %s - %s %s" % (caid, ecm_time, self.kurz(source))
							# oscam
							#oscsource = ecm_info.get("from", None)
							oscsource = ecm_info.get("reader", None)
							if oscsource:
								textvalue = " - %s - %s %s %s" % (caid, ecm_time, hops, self.kurz(oscsource))
							# gbox
							decode = ecm_info.get("decode", None)
							if decode:
								if decode == "Internal":
									textvalue = " - %s" % (caid)
								else:
									textvalue = " - %s - %s" % (caid, decode)
		return caidlist, textvalue
	getCaidlist = property(get_caidlist)

	def ecmfile(self):
		ecm = None
		info = {}
		service = self.source.service
		if service:
			frontendInfo = service.frontendInfo()
			if frontendInfo:
				try:
					ecmpath = "/tmp/ecm%s.info" % frontendInfo.getAll(False).get("tuner_number")
					ecm = open(ecmpath, "rb").readlines()
				except:
					try:
						ecm = open("/tmp/ecm.info", "rb").readlines()
					except: pass
			if ecm:
				for line in ecm:
					x = line.lower().find("msec")
					if x != -1:
						info["ecm time"] = line[0:x+4]
					else:
						item = line.split(":", 1)
						if len(item) > 1:
							info[item[0].strip().lower()] = item[1].strip()
						else:
							if not info.has_key("caid"):
								x = line.lower().find("caid")
								if x != -1:
									y = line.find(",")
									if y != -1:
										info["caid"] = line[x+5:y]
		return info

	def kurz(self, langTxt):
		if (len(langTxt)>31):
			retT = langTxt[:18]+".."
			return retT
		else:
			return langTxt

	def changed(self, what):
		if (what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo) or what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)
