from Components.Converter.Converter import Converter 
from Components.Element import cached
from Poll import Poll
from ServiceReference import ServiceReference 
from enigma import eServiceCenter, eServiceReference, iServiceInformation, iPlayableService, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable 
from string import upper 
from Components.ServiceEventTracker import ServiceEventTracker 
from Tools.Directories import fileExists, resolveFilename 
from os import environ, listdir, remove, rename, system 
from Components.ServiceEventTracker import ServiceEventTracker 

from SIFTeam.Extra.ServiceList import *
from SIFTeam.Extra.Emud import emud

import gettext

class ExtremeInfo(Poll, Converter, object):
	TUNERINFO = 0
	CAMNAME = 1
	NUMBER = 2
	ECMINFO = 3
	IRDCRYPT = 4
	SECACRYPT = 5
	NAGRACRYPT = 6
	VIACRYPT = 7
	CONAXCRYPT = 8
	BETACRYPT = 9
	CRWCRYPT = 10
	DREAMCRYPT = 11
	NDSCRYPT = 12
	IRDECM = 13
	SECAECM = 14
	NAGRAECM = 15
	VIAECM = 16
	CONAXECM = 17
	BETAECM = 18
	CRWECM = 19
	DREAMECM = 20
	NDSECM = 21
	CAIDINFO = 22
	FTA = 23
	EMU = 24
	CRD = 25
	NET = 26
	TUNERINFOBP = 27
	
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 2*1000
		self.poll_enabled = True

		self.list = []
		if (type == "TunerInfo"):
			self.type = self.TUNERINFO
		elif (type == "CamName"):
			self.type = self.CAMNAME
		elif (type == "Number"):
			self.type = self.NUMBER
			global servicelist
			if len(servicelist) == 0:
				initServiceList()
		elif (type == "EcmInfo"):
			self.type = self.ECMINFO
		elif (type == "CaidInfo"):
			self.type = self.CAIDINFO
		elif (type == "IrdCrypt"):
			self.type = self.IRDCRYPT
		elif (type == "SecaCrypt"):
			self.type = self.SECACRYPT
		elif (type == "NagraCrypt"):
			self.type = self.NAGRACRYPT
		elif (type == "ViaCrypt"):
			self.type = self.VIACRYPT
		elif (type == "ConaxCrypt"):
			self.type = self.CONAXCRYPT
		elif (type == "BetaCrypt"):
			self.type = self.BETACRYPT
		elif (type == "CrwCrypt"):
			self.type = self.CRWCRYPT
		elif (type == "DreamCrypt"):
			self.type = self.DREAMCRYPT
		elif (type == "NdsCrypt"):
			self.type = self.NDSCRYPT
		elif (type == "IrdEcm"):
			self.type = self.IRDECM
		elif (type == "SecaEcm"):
			self.type = self.SECAECM
		elif (type == "NagraEcm"):
			self.type = self.NAGRAECM
		elif (type == "ViaEcm"):
			self.type = self.VIAECM
		elif (type == "ConaxEcm"):
			self.type = self.CONAXECM
		elif (type == "BetaEcm"):
			self.type = self.BETAECM
		elif (type == "CrwEcm"):
			self.type = self.CRWECM
		elif (type == "DreamEcm"):
			self.type = self.DREAMECM
		elif (type == "NdsEcm"):
			self.type = self.NDSECM
		elif (type == "Fta"):
			self.type = self.FTA
		elif (type == "Emu"):
			self.type = self.EMU
		elif (type == "Crd"):
			self.type = self.CRD
		elif (type == "Net"):
			self.type = self.NET
		elif (type == "TunerInfoBP"):
			self.type = self.TUNERINFOBP
			
	@cached
	def getText(self):
		service = self.source.service
		info = (service and service.info())
		if (not info):
			return ""
		text = ""
		if ((self.type == self.TUNERINFO) or (self.type == self.TUNERINFOBP)):
			if (self.type == self.TUNERINFO):
				self.tunertype = "linelist"
				tunerinfo = self.getTunerInfo(service)
			else:
				self.tunertype = "lineslist"
				tunerinfo = self.getTunerInfo(service)
			text = tunerinfo
		elif (self.type == self.CAMNAME):
			text = emud.getInfoName()
		elif (self.type == self.NUMBER):
			text = self.getServiceNumber()
		elif (self.type == self.ECMINFO):
			text = emud.getInfoSystem()
		elif (self.type == self.CAIDINFO):
			text = emud.getInfoCaID
		return text
		
	text = property(getText)
	
	@cached
	def getBoolean(self):
		service = self.source.service
		info = (service and service.info())
		if (not info):
			return False
		if (self.type == self.IRDCRYPT):
			caemm = self.getIrdCrypt()
			return caemm
		elif (self.type == self.SECACRYPT):
			caemm = self.getSecaCrypt()
			return caemm
		elif (self.type == self.NAGRACRYPT):
			caemm = self.getNagraCrypt()
			return caemm
		elif (self.type == self.VIACRYPT):
			caemm = self.getViaCrypt()
			return caemm
		elif (self.type == self.CONAXCRYPT):
			caemm = self.getConaxCrypt()
			return caemm
		elif (self.type == self.BETACRYPT):
			caemm = self.getBetaCrypt()
			return caemm
		elif (self.type == self.CRWCRYPT):
			caemm = self.getCrwCrypt()
			return caemm
		elif (self.type == self.DREAMCRYPT):
			caemm = self.getDreamCrypt()
			return caemm
		elif (self.type == self.NDSCRYPT):
			caemm = self.getNdsCrypt()
			return caemm
		if (self.type == self.IRDECM):
			caemm = self.getIrdEcm()
			return caemm
		elif (self.type == self.SECAECM):
			caemm = self.getSecaEcm()
			return caemm
		elif (self.type == self.NAGRAECM):
			caemm = self.getNagraEcm()
			return caemm
		elif (self.type == self.VIAECM):
			caemm = self.getViaEcm()
			return caemm
		elif (self.type == self.CONAXECM):
			caemm = self.getConaxEcm()
			return caemm
		elif (self.type == self.BETAECM):
			caemm = self.getBetaEcm()
			return caemm
		elif (self.type == self.CRWECM):
			caemm = self.getCrwEcm()
			return caemm
		elif (self.type == self.DREAMECM):
			caemm = self.getDreamEcm()
			return caemm
		elif (self.type == self.NDSECM):
			caemm = self.getNdsEcm()
			return caemm
		elif (self.type == self.FTA):
			caemm = self.getFta()
			return caemm
		elif (self.type == self.EMU):
			caemm = self.getEmu()
			return caemm
		elif (self.type == self.CRD):
			caemm = self.getCrd()
			return caemm
		elif (self.type == self.NET):
			caemm = self.getNet()
			return caemm
		return False
		
	boolean = property(getBoolean)
	
	def getFta(self):
		if emud.getInfoProtocol()[:3].lower() == "fta":
			return True
			
		if emud.getInfoCaID() == "":
			return True
			
		return False
		
	def getEmu(self):
		if emud.getInfoProtocol()[:3].lower() == "emu":
			return True
		
		return False
		
	def getCrd(self):
		if emud.getInfoProtocol()[:3].lower() == "sci":
			return True
		
		if emud.getInfoProtocol()[:4].lower() == "card":
			return True
			
		return False
		
	def getNet(self):
		if emud.getInfoProtocol()[:3].lower() == "net":
			return True
			
		if not self.getEmu() and not self.getCrd():
			return True
			
		return False
		
	def getIrdEcm(self):
		if emud.getInfoSystemByte() == "6":
			return True
				
		return False
		
	def getSecaEcm(self):
		if emud.getInfoSystemByte() == "1":
			return True
				
		return False
		
	def getNagraEcm(self):
		if emud.getInfoSystemByte() == "18":
			return True
				
		return False
		
	def getViaEcm(self):
		if emud.getInfoSystemByte() == "5":
			return True
				
		return False
		
	def getConaxEcm(self):
		if emud.getInfoSystemByte() == "B":
			return True
				
		return False
		
	def getBetaEcm(self):
		if emud.getInfoSystemByte() == "17":
			return True
				
		return False
		
	def getCrwEcm(self):
		if emud.getInfoSystemByte() == "D":
			return True
				
		return False
		
	def getDreamEcm(self):
		if emud.getInfoSystemByte() == "4A":
			return True
				
		return False
		
	def getNdsEcm(self):
		if emud.getInfoSystemByte() == "9":
			return True
				
		return False
		
	def checkCAID(self, value):
		try:
			service = self.source.service
			if service:
				info = (service and service.info())
				if info:
					caids = info.getInfoObject(iServiceInformation.sCAIDs)
					if caids:
						if (len(caids) > 0):
							for caid in caids:
								caid = self.int2hex(caid)
								if (len(caid) == 3):
									caid = ("0%s" % caid)
								caid = caid[:2]
								caid = caid.upper()
								if (caid == value):
									return True
		except Exception:
			return False
		
		return False
		
	def getIrdCrypt(self):
		return self.checkCAID("06")
		
	def getSecaCrypt(self):
		return self.checkCAID("01")
	
	def getNagraCrypt(self):
		return self.checkCAID("18")
	
	def getViaCrypt(self):
		return self.checkCAID("05")
	
	def getConaxCrypt(self):
		return self.checkCAID("0B")
	
	def getBetaCrypt(self):
		return self.checkCAID("17")
	
	def getCrwCrypt(self):
		return self.checkCAID("0D")
	
	def getDreamCrypt(self):
		return self.checkCAID("4A")
	
	def getNdsCrypt(self):
		return self.checkCAID("09")
	
	def int2hex(self, int):
		return ("%x" % int)
	
	def changed(self, what):
		Converter.changed(self, what)
		
	def getServiceNumber(self):
		global servicelist
		global radioservicelist
		service = self.source.service
		info = service and service.info()
		if info is None:
			return ""
		
		name = info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
		
		list = []
		if info.getInfoString(iServiceInformation.sServiceref).startswith("1:0:2"):
			list = radioservicelist
		elif info.getInfoString(iServiceInformation.sServiceref).startswith("1:0:1"):
			list = servicelist
		
		if name in list:
			for idx in range(1, len(list)):
				if name == list[idx-1]:
					return str(idx)
		else:
			return ""
		
	def getTunerInfo(self, service):
		tunerinfo = ""
		feinfo = (service and service.frontendInfo())
		if (feinfo is not None):
			frontendData = (feinfo and feinfo.getAll(True))
			if (frontendData is not None):
				if ((frontendData.get("tuner_type") == "DVB-S") or (frontendData.get("tuner_type") == "DVB-C")):
					frequency = (str((frontendData.get("frequency") / 1000)) + " MHz")
					symbolrate = str(int((frontendData.get("symbol_rate", 0) / 1000)))
					if (frontendData.get("tuner_type") == "DVB-S"):
						try:
							orb = {3590: "Thor/Intelsat (1.0W)",
							 3560: "Amos (4.0W)",
							 3550: "Atlantic Bird (5.0W)",
							 3530: "Nilesat/Atlantic Bird (7.0W)",
							 3520: "Atlantic Bird (8.0W)",
							 3475: "Atlantic Bird (12.5W)",
							 3460: "Express (14.0W)",
							 3450: "Telstar (15.0W)",
							 3420: "Intelsat (18.0W)",
							 3380: "Nss (22.0W)",
							 3355: "Intelsat (24.5W)",
							 3325: "Intelsat (27.5W)",
							 3300: "Hispasat (30.0W)",
							 3285: "Intelsat (31.5W)",
							 3170: "Intelsat (43.0W)",
							 3150: "Intelsat (45.0W)",
							 3070: "Intelsat (53.0W)",
							 3045: "Intelsat (55.5W)",
							 3020: "Intelsat 9 (58.0W)",
							 2990: "Amazonas (61.0W)",
							 2900: "Star One (70.0W)",
							 2880: "AMC 6 (72.0W)",
							 2875: "Echostar 6 (72.7W)",
							 2860: "Horizons (74.0W)",
							 2810: "AMC5 (79.0W)",
							 2780: "NIMIQ 4 (82.0W)",
							 2690: "NIMIQ 1 (91.0W)",
							 3592: "Thor/Intelsat (0.8W)",
							 2985: "Echostar 3,12 (61.5W)",
							 2830: "Echostar 8 (77.0W)",
							 2630: "Galaxy 19 (97.0W)",
							 2500: "Echostar 10,11 (110.0W)",
							 2502: "DirectTV 5 (110.0W)",
							 2410: "Echostar 7 Anik F3 (119.0W)",
							 2391: "Galaxy 23 (121.0W)",
							 2390: "Echostar 9 (121.0W)",
							 2412: "DirectTV 7S (119.0W)",
							 2310: "Galaxy 27 (129.0W)",
							 2311: "Ciel 2 (129.0W)",
							 2120: "Echostar 2 (148.0W)",
							 1100: "BSat 1A,2A (110.0E)",
							 1101: "N-Sat 110 (110.0E)",
							 1131: "KoreaSat 5 (113.0E)",
							 1440: "SuperBird 7,C2 (144.0E)",
							 1006: "AsiaSat 2 (100.5E)",
							 1030: "Express A2 (103.0E)",
							 1056: "Asiasat 3S (105.5E)",
							 1082: "NSS 11 (108.2E)",
							 881: "ST1 (88.0E)",
							 900: "Yamal 201 (90.0E)",
							 917: "Mesat (91.5E)",
							 950: "Insat 4B (95.0E)",
							 951: "NSS 6 (95.0E)",
							 765: "Telestar (76.5E)",
							 785: "ThaiCom 5 (78.5E)",
							 800: "Express (80.0E)",
							 830: "Insat 4A (83.0E)",
							 850: "Intelsat 709 (85.2E)",
							 750: "Abs (75.0E)",
							 720: "Intelsat (72.0E)",
							 705: "Eutelsat W5 (70.5E)",
							 685: "Intelsat (68.5E)",
							 620: "Intelsat 902 (62.0E)",
							 600: "Intelsat 904 (60.0E)",
							 570: "Nss (57.0E)",
							 530: "Express AM22 (53.0E)",
							 480: "Eutelsat 2F2 (48.0E)",
							 450: "Intelsat (45.0E)",
							 420: "Turksat 2A (42.0E)",
							 400: "Express AM1 (40.0E)",
							 390: "Hellas Sat 2 (39.0E)",
							 380: "Paksat 1 (38.0E)",
							 360: "Eutelsat Sesat (36.0E)",
							 335: "Astra 1M (33.5E)",
							 330: "Eurobird 3 (33.0E)",
							 328: "Galaxy 11 (32.8E)",
							 315: "Astra 5A (31.5E)",
							 310: "Turksat (31.0E)",
							 305: "Arabsat (30.5E)",
							 285: "Eurobird 1 (28.5E)",
							 284: "Eurobird/Astra (28.2E)",
							 282: "Eurobird/Astra (28.2E)",
							 1220: "AsiaSat (122.0E)",
							 1380: "Telstar 18 (138.0E)",
							 260: "Badr 3/4 (26.0E)",
							 255: "Eurobird 2 (25.5E)",
							 235: "Astra 1E (23.5E)",
							 215: "Eutelsat (21.5E)",
							 216: "Eutelsat W6 (21.6E)",
							 210: "AfriStar 1 (21.0E)",
							 192: "Astra 1F (19.2E)",
							 160: "Eutelsat W2 (16.0E)",
							 130: "Hot Bird 6,7A,8 (13.0E)",
							 100: "Eutelsat W1 (10.0E)",
							 90: "Eurobird 9 (9.0E)",
							 70: "Eutelsat W3A (7.0E)",
							 50: "Sirius 4 (5.0E)",
							 48: "Sirius 4 (4.8E)",
							 30: "Telecom 2 (3.0E)"}[frontendData.get("orbital_position", "None")]
						except:
							orb = ("Unsupported SAT: %s" % str([frontendData.get("orbital_position", "None")]))
						if (self.tunertype == "linelist"):
							pol = {eDVBFrontendParametersSatellite.Polarisation_Horizontal: "H",
							 eDVBFrontendParametersSatellite.Polarisation_Vertical: "V",
							 eDVBFrontendParametersSatellite.Polarisation_CircularLeft: "CL",
							 eDVBFrontendParametersSatellite.Polarisation_CircularRight: "CR"}[frontendData.get("polarization", eDVBFrontendParametersSatellite.Polarisation_Horizontal)]
						else:
							pol = {eDVBFrontendParametersSatellite.Polarisation_Horizontal: "Horizontal",
							 eDVBFrontendParametersSatellite.Polarisation_Vertical: "Vertical",
							 eDVBFrontendParametersSatellite.Polarisation_CircularLeft: "Circular Left",
							 eDVBFrontendParametersSatellite.Polarisation_CircularRight: "Circular Right"}[frontendData.get("polarization", eDVBFrontendParametersSatellite.Polarisation_Horizontal)]
						fec = {eDVBFrontendParametersSatellite.FEC_None: "None",
						 eDVBFrontendParametersSatellite.FEC_Auto: "Auto",
						 eDVBFrontendParametersSatellite.FEC_1_2: "1/2",
						 eDVBFrontendParametersSatellite.FEC_2_3: "2/3",
						 eDVBFrontendParametersSatellite.FEC_3_4: "3/4",
						 eDVBFrontendParametersSatellite.FEC_5_6: "5/6",
						 eDVBFrontendParametersSatellite.FEC_7_8: "7/8",
						 eDVBFrontendParametersSatellite.FEC_3_5: "3/5",
						 eDVBFrontendParametersSatellite.FEC_4_5: "4/5",
						 eDVBFrontendParametersSatellite.FEC_8_9: "8/9",
						 eDVBFrontendParametersSatellite.FEC_9_10: "9/10"}[frontendData.get("fec_inner", eDVBFrontendParametersSatellite.FEC_Auto)]
						if (self.tunertype == "linelist"):
							tunerinfo = ((((((((frequency + "  ") + pol) + "  ") + fec) + "  ") + symbolrate) + "  ") + orb)
						else:
							tunerinfo = ((((((((("Satellite: " + orb) + "\nFrequency: ") + frequency) + "\nPolarisation: ") + pol) + "\nSymbolrate: ") + symbolrate) + "\nFEC: ") + fec)
					elif (frontendData.get("tuner_type") == "DVB-C"):
						fec = {eDVBFrontendParametersCable.FEC_None: "None",
						 eDVBFrontendParametersCable.FEC_Auto: "Auto",
						 eDVBFrontendParametersCable.FEC_1_2: "1/2",
						 eDVBFrontendParametersCable.FEC_2_3: "2/3",
						 eDVBFrontendParametersCable.FEC_3_4: "3/4",
						 eDVBFrontendParametersCable.FEC_5_6: "5/6",
						 eDVBFrontendParametersCable.FEC_7_8: "7/8",
						 eDVBFrontendParametersCable.FEC_8_9: "8/9"}[frontendData.get("fec_inner", eDVBFrontendParametersCable.FEC_Auto)]
						if (self.tunertype == "linelist"):
							tunerinfo = ((((frequency + "  ") + fec) + "  ") + symbolrate)
						else:
							tunerinfo = ((((("Frequency: " + frequency) + "\nSymbolrate: ") + symbolrate) + "\nFEC: ") + fec)
					elif (self.tunertype == "linelist"):
						tunerinfo = ((frequency + "  ") + symbolrate)
					else:
						tunerinfo = ((("Frequency: " + frequency) + "\nSymbolrate: ") + symbolrate)
					return tunerinfo
			else:
				return ""
			