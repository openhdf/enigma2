# -*- coding: utf-8 -*-
#
# ChannelExpertInfo Converter by mcbain // v0.1 // 20111109
#
from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable, eDVBFrontendParametersTerrestrial
from Components.Element import cached
from Components.ServiceEventTracker import ServiceEventTracker

class ChannelExpertInfo(Converter, object):
	TUNERINFO = 0
	TUNERINFOBP = 1
	TUNERTYPE = 2
	ORBITALPOSITION = 3

	def __init__(self, type):
		Converter.__init__(self, type)

		if type == 'TunerInfo':
			self.type = self.TUNERINFO
		elif type == 'TunerInfoBP':
			self.type = self.TUNERINFOBP
		elif type == 'TunerType':
			self.type = self.TUNERTYPE
		elif type == "OrbitalPosition":
			self.type = self.ORBITALPOSITION

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ''

		if (self.type == self.TUNERINFO):
			self.tunertype = 'linelist'
			tunerinfo = self.getTunerInfo(service)
			text = tunerinfo
		elif (self.type == self.TUNERINFOBP):
			self.tunertype = 'lineslist'
			tunerinfo = self.getTunerInfo(service)
			text = tunerinfo
		elif (self.type == self.TUNERTYPE):
			self.tunertype = 'tunertype'
			tunerinfo = self.getTunerInfo(service)
			text = tunerinfo
		elif self.type == self.ORBITALPOSITION:
			orbital = self.getOrbitalPosition(info)
			text = orbital
		return text

	text = property(getText)

	def getTunerInfo(self, service):
		tunerinfo = ''
		feinfo = (service and service.frontendInfo())
		if (feinfo is not None):
			frontendData = (feinfo and feinfo.getAll(True))
			if (frontendData is not None):
				if ((frontendData.get('tuner_type') == 'DVB-S') or (frontendData.get('tuner_type') == 'DVB-C')):
					frequency = (str((frontendData.get('frequency') / 1000)) + ' MHz')
					symbolrate = str(int((frontendData.get('symbol_rate', 0) / 1000)))
					if (frontendData.get('tuner_type') == 'DVB-S'):
						try:
							orb = {
							 3590: "Thor/Intelsat (1.0W)",
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
							 30: "Telecom 2 (3.0E)"
							}[frontendData.get('orbital_position', 'None')]
						except:
							orbital_pos = float(frontendData["orbital_position"])
							if orbital_pos > 1800:
								orb_pos = str((float(3600 - orbital_pos)) / 10.0) + "° W"
							elif orbital_pos > 0:
								orb_pos = str((float(orbital_pos)) / 10.0) + "° E"
							orb = ('Unsupported SAT (%s)' % str(orb_pos))
						if (self.tunertype == 'linelist'):
							pol = {
							 eDVBFrontendParametersSatellite.Polarisation_Horizontal: "H",
							 eDVBFrontendParametersSatellite.Polarisation_Vertical: "V",
							 eDVBFrontendParametersSatellite.Polarisation_CircularLeft: "CL",
							 eDVBFrontendParametersSatellite.Polarisation_CircularRight: "CR"
							}[frontendData.get('polarization', eDVBFrontendParametersSatellite.Polarisation_Horizontal)]
						else:
							pol = {
							 eDVBFrontendParametersSatellite.Polarisation_Horizontal: "Horizontal",
							 eDVBFrontendParametersSatellite.Polarisation_Vertical: "Vertical",
							 eDVBFrontendParametersSatellite.Polarisation_CircularLeft: "Circular Left",
							 eDVBFrontendParametersSatellite.Polarisation_CircularRight: "Circular Right"
							}[frontendData.get('polarization', eDVBFrontendParametersSatellite.Polarisation_Horizontal)]

						fec = {
						 eDVBFrontendParametersSatellite.FEC_None: "None",
						 eDVBFrontendParametersSatellite.FEC_Auto: "Auto",
						 eDVBFrontendParametersSatellite.FEC_1_2: "1/2",
						 eDVBFrontendParametersSatellite.FEC_2_3: "2/3",
						 eDVBFrontendParametersSatellite.FEC_3_4: "3/4",
						 eDVBFrontendParametersSatellite.FEC_5_6: "5/6",
						 eDVBFrontendParametersSatellite.FEC_7_8: "7/8",
						 eDVBFrontendParametersSatellite.FEC_3_5: "3/5",
						 eDVBFrontendParametersSatellite.FEC_4_5: "4/5",
						 eDVBFrontendParametersSatellite.FEC_8_9: "8/9",
						 eDVBFrontendParametersSatellite.FEC_9_10: "9/10"
						}[frontendData.get('fec_inner', eDVBFrontendParametersSatellite.FEC_Auto)]
						system = {
						 eDVBFrontendParametersSatellite.System_DVB_S: 'DVB-S',
						 eDVBFrontendParametersSatellite.System_DVB_S2: 'DVB-S2'
						}[frontendData.get('system', eDVBFrontendParametersSatellite.System_DVB_S)]
						modulation = {
						 eDVBFrontendParametersSatellite.Modulation_Auto : 'Auto',
						 eDVBFrontendParametersSatellite.Modulation_QPSK : 'QPSK',
						 eDVBFrontendParametersSatellite.Modulation_8PSK : '8PSK',
						 eDVBFrontendParametersSatellite.Modulation_QAM16 : 'QAM16',
						}[frontendData.get('modulation', eDVBFrontendParametersSatellite.Modulation_Auto)]
						if (self.tunertype == 'linelist'):
							tunerinfo = frequency + '  ' + pol + '  ' + fec + '  ' + symbolrate + '  ' + orb
						elif (self.tunertype == 'tunertype'):
							tunerinfo = system + '  ' + modulation
						elif (self.tunertype == 'lineslist'):
							tunerinfo = 'Satellite: ' + orb + '\nFrequency: ' + frequency + '\nPolarisation: ' + pol + '\nSymbolrate: ' + symbolrate + '\nFEC: ' + fec
					elif (frontendData.get('tuner_type') == 'DVB-C'):
						fec = {
						 eDVBFrontendParametersCable.FEC_None: "None",
						 eDVBFrontendParametersCable.FEC_Auto: "Auto",
						 eDVBFrontendParametersCable.FEC_1_2: "1/2",
						 eDVBFrontendParametersCable.FEC_2_3: "2/3",
						 eDVBFrontendParametersCable.FEC_3_4: "3/4",
						 eDVBFrontendParametersCable.FEC_5_6: "5/6",
						 eDVBFrontendParametersCable.FEC_7_8: "7/8",
						 eDVBFrontendParametersCable.FEC_8_9: "8/9"
						}[frontendData.get('fec_inner', eDVBFrontendParametersCable.FEC_Auto)]
						modulation = {
						 eDVBFrontendParametersCable.Modulation_Auto: "Auto",
						 eDVBFrontendParametersCable.Modulation_QAM16 : "QAM16",
						 eDVBFrontendParametersCable.Modulation_QAM32 : "QAM32",
						 eDVBFrontendParametersCable.Modulation_QAM64 : "QAM64",
						 eDVBFrontendParametersCable.Modulation_QAM128 : "QAM128",
						 eDVBFrontendParametersCable.Modulation_QAM256 : "QAM256"
						}[frontendData.get('modulation', eDVBFrontendParametersCable.Modulation_Auto)]
						if (self.tunertype == 'linelist'):
							tunerinfo = frequency + '  ' + symbolrate + '  ' + modulation
						elif (self.tunertype == 'tunertype'):
							tunerinfo = 'DVB-C' + '  ' + modulation
						elif (self.tunertype == 'lineslist'):
							tunerinfo = 'Frequency: ' + frequency + '\nSymbolrate: ' + symbolrate + '\nModulation: ' + modulation + '\nFEC: ' + fec
					elif (frontendData.get('tuner_type') == 'DVB-T'):
						bandwidth = {
						 eDVBFrontendParametersTerrestrial.Bandwidth_Auto : "Auto",
						 eDVBFrontendParametersTerrestrial.Bandwidth_8MHz : "8 MHz",
						 eDVBFrontendParametersTerrestrial.Bandwidth_7MHz : "7 MHz",
						 eDVBFrontendParametersTerrestrial.Bandwidth_6MHz : "6 MHz"
						}[frontendData.get('bandwidth', eDVBFrontendParametersTerrestrial.Bandwidth_Auto)]
						code_rate_lp = {
						 eDVBFrontendParametersTerrestrial.FEC_Auto : "Auto",
						 eDVBFrontendParametersTerrestrial.FEC_1_2 : "1/2",
						 eDVBFrontendParametersTerrestrial.FEC_2_3 : "2/3",
						 eDVBFrontendParametersTerrestrial.FEC_3_4 : "3/4",
						 eDVBFrontendParametersTerrestrial.FEC_5_6 : "5/6",
						 eDVBFrontendParametersTerrestrial.FEC_7_8 : "7/8"
						}[frontendData.get('code_rate_lp', eDVBFrontendParametersTerrestrial.FEC_Auto)]
						code_rate_hp = {
						 eDVBFrontendParametersTerrestrial.FEC_Auto : "Auto",
						 eDVBFrontendParametersTerrestrial.FEC_1_2 : "1/2",
						 eDVBFrontendParametersTerrestrial.FEC_2_3 : "2/3",
						 eDVBFrontendParametersTerrestrial.FEC_3_4 : "3/4",
						 eDVBFrontendParametersTerrestrial.FEC_5_6 : "5/6",
						 eDVBFrontendParametersTerrestrial.FEC_7_8 : "7/8"
						}[frontendData.get('code_rate_hp', eDVBFrontendParametersTerrestrial.FEC_Auto)]
						modulation = {
						 eDVBFrontendParametersTerrestrial.Modulation_Auto : "Auto",
						 eDVBFrontendParametersTerrestrial.Modulation_QPSK : "QPSK",
						 eDVBFrontendParametersTerrestrial.Modulation_QAM16 : "QAM16",
						 eDVBFrontendParametersTerrestrial.Modulation_QAM64 : "QAM64"
						}[frontendData.get('constellation', eDVBFrontendParametersTerrestrial.Modulation_Auto)]
						if code_rate_lp:
							fec = code_rate_lp
						elif code_rate_hp:
							fec = code_rate_hp
						else:
							fec = ''
						if (self.tunertype == 'linelist'):
							tunerinfo = frequency + '  ' + modulation + '  ' + fec + '  ' + symbolrate + '  ' + bandwidth
						elif (self.tunertype == 'tunertype'):
							tunerinfo = 'DVB-T' + '  ' + modulation
						elif (self.tunertype == 'lineslist'):
							tunerinfo = 'Bandwidth: ' + bandwidth + '\nFrequency: ' + frequency + '\nModulation: ' + modulation + '\nSymbolrate: ' + symbolrate + '\nFEC: ' + fec
					else:
						if (self.tunertype == 'linelist'):
							tunerinfo = frequency + '  ' + symbolrate
						elif (self.tunertype == 'tunertype'):
							tunerinfo = 'Unknown'
						elif (self.tunertype == 'lineslist'):
							tunerinfo = 'Frequency: ' + frequency + '\nSymbolrate: ' + symbolrate
					return tunerinfo
			else:
				return ''

	def getOrbitalPosition(self, info):
		transponderData = info.getInfoObject(iServiceInformation.sTransponderData)
		orbital = 0
		if transponderData is not None:
			if isinstance(transponderData, float):
				return ''
			if transponderData.has_key('tuner_type'):
				if transponderData['tuner_type'] == 'DVB-S':
					orbital = float(transponderData['orbital_position'])
					if orbital > 1800:
						orbital = str((float(3600 - orbital)) / 10.0) + '° W'
					else:
						orbital = str((float(orbital)) / 10.0) + '° E'
					return orbital
		return ''
