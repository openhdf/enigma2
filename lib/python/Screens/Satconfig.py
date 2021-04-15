from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from enigma import eDVBDB, eDVBResourceManager, getLinkedSlotID, isFBCLink
from Screens.Screen import Screen
from Components.SystemInfo import SystemInfo
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.NimManager import nimmanager
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.SelectionList import SelectionList, SelectionEntryComponent
from Components.config import getConfigListEntry, config, configfile, ConfigNothing, ConfigSatlist, ConfigYesNo, ConfigSubsection, ConfigSelection
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.Sources.Boolean import Boolean
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.ServiceStopScreen import ServiceStopScreen
from Screens.AutoDiseqc import AutoDiseqc
from Tools.BoundFunction import boundFunction
from boxbranding import getBoxType

from time import mktime, localtime
from datetime import datetime
from os import path
import six

from Tools.BugHunting import printCallSequence


def setForceLNBPowerChanged(configElement):
	f = open("/proc/stb/frontend/fbc/force_lnbon", "w")
	if configElement.value:
		f.write("on")
	else:
		f.write("off")
	f.close()


def setForceToneBurstChanged(configElement):
	f = open("/proc/stb/frontend/fbc/force_toneburst", "w")
	if configElement.value:
		f.write("enable")
	else:
		f.write("disable")
	f.close()


config.tunermisc = ConfigSubsection()
if SystemInfo["ForceLNBPowerChanged"]:
	config.tunermisc.forceLnbPower = ConfigYesNo(default=False)
	config.tunermisc.forceLnbPower.addNotifier(setForceLNBPowerChanged)

if SystemInfo["ForceToneBurstChanged"]:
	config.tunermisc.forceToneBurst = ConfigYesNo(default=False)
	config.tunermisc.forceToneBurst.addNotifier(setForceToneBurstChanged)


class TunerSetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		self.setup_title = _("Tuner settings")
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)
		self['footnote'] = Label()

		self.onChangedEntry = []

		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)

		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions", "MenuActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"save": self.apply,
				"menu": self.closeRecursive,
			}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["description"] = Label("")

		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def createSetup(self):
		level = config.usage.setup_level.index

		self.list = []

		if level >= 1:
			if SystemInfo["ForceLNBPowerChanged"]:
				self.list.append(getConfigListEntry(_("Force LNB Power"), config.tunermisc.forceLnbPower, _("Force LNB Tuner Power settings.")))
			if SystemInfo["ForceToneBurstChanged"]:
				self.list.append(getConfigListEntry(_("Force ToneBurst"), config.tunermisc.forceToneBurst, _("Force LNB Tuner ToneBurst settings.")))

		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if config.usage.sort_settings.value:
			self["config"].list.sort()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def confirm(self, confirmed):
		self.keySave()

	def apply(self):
		self.keySave()

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary


class NimSetup(Screen, ConfigListScreen, ServiceStopScreen):
	def createSimpleSetup(self, list, mode):
		nim = self.nimConfig.dvbs

		if mode == "single":
			self.singleSatEntry = getConfigListEntry(_("Satellite"), nim.diseqcA, _("Select the satellite your dish receives from. If you are unsure select 'automatic' and the receiver will attempt to determine this for you."))
			list.append(self.singleSatEntry)
			if nim.diseqcA.value in ("360", "560"):
				list.append(getConfigListEntry(_("Use circular LNB"), nim.simpleDiSEqCSetCircularLNB, _("If you are using a Circular polarised LNB select 'yes', otherwise select 'no'.")))
			list.append(getConfigListEntry(_("Send DiSEqC"), nim.simpleSingleSendDiSEqC, _("Only select 'yes' if you are using a multiswich that requires a DiSEqC Port-A command signal. For all other setups select 'no'.")))
		else:
			list.append(getConfigListEntry(_("Port A"), nim.diseqcA, _("Select the satellite which is connected to Port-A of your switch. If you are unsure select 'automatic' and the receiver will attempt to determine this for you. If nothing is connected to this port, select 'nothing connected'.")))

		if mode in ("toneburst_a_b", "diseqc_a_b", "diseqc_a_b_c_d"):
			list.append(getConfigListEntry(_("Port B"), nim.diseqcB, _("Select the satellite which is connected to Port-B of your switch. If you are unsure select 'automatic' and the receiver will attempt to determine this for you. If nothing is connected to this port, select 'nothing connected'.")))
			if mode == "diseqc_a_b_c_d":
				list.append(getConfigListEntry(_("Port C"), nim.diseqcC, _("Select the satellite which is connected to Port-C of your switch. If you are unsure select 'automatic' and the receiver will attempt to determine this for you. If nothing is connected to this port, select 'nothing connected'.")))
				list.append(getConfigListEntry(_("Port D"), nim.diseqcD, _("Select the satellite which is connected to Port-D of your switch. If you are unsure select 'automatic' and the receiver will attempt to determine this for you. If nothing is connected to this port, select 'nothing connected'.")))
			if mode != "toneburst_a_b":
				list.append(getConfigListEntry(_("Set voltage and 22KHz"), nim.simpleDiSEqCSetVoltageTone, _("Leave this set to 'yes' unless you fully understand why you are adjusting it.")))
				list.append(getConfigListEntry(_("Send DiSEqC only on satellite change"), nim.simpleDiSEqCOnlyOnSatChange, _("Select 'yes' to only send the DiSEqC command when changing from one satellite to another, or select 'no' for the DiSEqC command to be resent on every zap.")))

	def createPositionerSetup(self, list):
		nim = self.nimConfig.dvbs
		if nim.diseqcMode.value == "positioner_select":
			self.selectSatsEntry = getConfigListEntry(_("Press OK to select satellites"), nim.pressOKtoList, _("Press OK to select a group of satellites to configure in one block."))
			list.append(self.selectSatsEntry)
		list.append(getConfigListEntry(_("Longitude"), nim.longitude, _("Enter your current longitude. This is the number of degrees you are from zero meridian as a decimal.")))
		list.append(getConfigListEntry(" ", nim.longitudeOrientation, _("Enter if you are in the east or west hemisphere.")))
		list.append(getConfigListEntry(_("Latitude"), nim.latitude, _("Enter your current latitude. This is the number of degrees you are from the equator as a decimal.")))
		list.append(getConfigListEntry(" ", nim.latitudeOrientation, _("Enter if you are north or south of the equator.")))
		if SystemInfo["CanMeasureFrontendInputPower"]:
			self.advancedPowerMeasurement = getConfigListEntry(_("Use power measurement"), nim.powerMeasurement, _("Power management. Consult your receiver's manual for more information."))
			list.append(self.advancedPowerMeasurement)
			if nim.powerMeasurement.value:
				list.append(getConfigListEntry(_("Power threshold in mA"), nim.powerThreshold, _("Power threshold. Consult your receiver's manual for more information.")))
				self.turningSpeed = getConfigListEntry(_("Rotor turning speed"), nim.turningSpeed, _("Select how quickly the dish should move between satellites."))
				list.append(self.turningSpeed)
				if nim.turningSpeed.value == "fast epoch":
					self.turnFastEpochBegin = getConfigListEntry(_("Begin time"), nim.fastTurningBegin, _("Only move the dish quickly after this hour."))
					self.turnFastEpochEnd = getConfigListEntry(_("End time"), nim.fastTurningEnd, _("Only move the dish quickly before this hour."))
					list.append(self.turnFastEpochBegin)
					list.append(self.turnFastEpochEnd)
		else:
			if nim.powerMeasurement.value:
				nim.powerMeasurement.value = False
				nim.powerMeasurement.save()
		if not hasattr(self, 'additionalMotorOptions'):
			self.additionalMotorOptions = ConfigYesNo(False)
		self.showAdditionalMotorOptions = getConfigListEntry(_("Extra motor options"), self.additionalMotorOptions, _("Additional motor options allow you to enter details from your motor's spec sheet so enigma can work out how long it will take to move the dish from one satellite to another satellite."))
		self.list.append(self.showAdditionalMotorOptions)
		if self.additionalMotorOptions.value:
			self.list.append(getConfigListEntry("   " + _("Horizontal turning speed") + " [" + chr(176) + _("/sec]"), nim.turningspeedH, _("Consult your motor's spec sheet for this information, or leave the default setting.")))
			self.list.append(getConfigListEntry("   " + _("Vertical turning speed") + " [" + chr(176) + _("/sec]"), nim.turningspeedV, _("Consult your motor's spec sheet for this information, or leave the default setting.")))
			self.list.append(getConfigListEntry("   " + _("Turning step size") + " [" + chr(176) + "]", nim.tuningstepsize, _("Consult your motor's spec sheet for this information, or leave the default setting.")))
			self.list.append(getConfigListEntry("   " + _("Max memory positions"), nim.rotorPositions, _("Consult your motor's spec sheet for this information, or leave the default setting.")))

	def createConfigMode(self):
		if self.nim.canBeCompatible("DVB-S"):
			choices = {"nothing": _("not configured"),
						"simple": _("Simple"),
						"advanced": _("Advanced")}
			if len(nimmanager.canEqualTo(self.slotid)) > 0:
				choices["equal"] = _("Equal to")
			if len(nimmanager.canDependOn(self.slotid)) > 0:
				choices["satposdepends"] = _("Second cable of motorized LNB")
			if len(nimmanager.canConnectTo(self.slotid)) > 0:
				choices["loopthrough"] = _("Loop through to")
			if isFBCLink(self.nim.slot):
				choices = {"nothing": _("not configured"),
						"advanced": _("Advanced")}
			if self.nim.isMultiType():
				self.nimConfig.dvbs.configMode.setChoices(choices, default="nothing")
			else:
				self.nimConfig.dvbs.configMode.setChoices(choices, default="simple")

	def createSetup(self):
		print("Creating setup")
		self.list = []

		self.multiType = None
		self.diseqcModeEntry = None
		self.advancedSatsEntry = None
		self.advancedLnbsEntry = None
		self.advancedDiseqcMode = None
		self.advancedUsalsEntry = None
		self.advancedLof = None
		self.advancedPowerMeasurement = None
		self.turningSpeed = None
		self.turnFastEpochBegin = None
		self.turnFastEpochEnd = None
		self.toneburst = None
		self.committedDiseqcCommand = None
		self.uncommittedDiseqcCommand = None
		self.commandOrder = None
		self.cableScanType = None
		self.have_advanced = False
		self.advancedUnicable = None
		self.advancedType = None
		self.advancedManufacturer = None
		self.advancedSCR = None
		self.advancedDiction = None
		self.advancedConnected = None
		self.advancedUnicableTuningAlgo = None
		self.showAdditionalMotorOptions = None
		self.selectSatsEntry = None
		self.advancedSelectSatsEntry = None
		self.singleSatEntry = None
		self.terrestrialRegionsEntry = None
		self.cableRegionsEntry = None

		if not hasattr(self, "terrestrialCountriesEntry"):
			self.terrestrialCountriesEntry = None
		if not hasattr(self, "cableCountriesEntry"):
			self.cableCountriesEntry = None

		if self.nim.isMultiType():
			try:
				multiType = self.nimConfig.multiType
				choices = "("
				for x in multiType.choices.choices:		# Set list entry corresponding to the current tuner type
					if self.nim.isCompatible(x[1]):
						multiType.setValue(x[0])
					choices += x[1]
					choices += ", "
				choices = choices[:-2] + ")"
				self.multiType = getConfigListEntry(_("Tuner type %s") % (choices), multiType, _("You can switch with left and right this tuner types %s") % (choices))
				self.list.append(self.multiType)
			except:
				self.multiType = None

		if self.nim.isCompatible("DVB-S"):
			nimConfig = self.nimConfig.dvbs
			self.configMode = getConfigListEntry(_("Configuration mode"), nimConfig.configMode, _("Configure this tuner using simple or advanced options, or loop it through to another tuner, or copy a configuration from another tuner, or disable it."))
			self.list.append(self.configMode)

			if nimConfig.configMode.value == "simple":			#simple setup
				self.diseqcModeEntry = getConfigListEntry(pgettext(_("Satellite configuration mode"), _("Mode")), nimConfig.diseqcMode, _("Select how the satellite dish is set up. i.e. fixed dish, single LNB, DiSEqC switch, positioner, etc."))
				self.list.append(self.diseqcModeEntry)
				if nimConfig.diseqcMode.value in ("single", "toneburst_a_b", "diseqc_a_b", "diseqc_a_b_c_d"):
					self.createSimpleSetup(self.list, nimConfig.diseqcMode.value)
				if nimConfig.diseqcMode.value in ("positioner", "positioner_select"):
					self.createPositionerSetup(self.list)
			elif nimConfig.configMode.value == "equal":
				choices = []
				nimlist = nimmanager.canEqualTo(self.nim.slot)
				for id in nimlist:
					choices.append((str(id), nimmanager.getNimDescription(id)))
				nimConfig.connectedTo.setChoices(choices)
				self.list.append(getConfigListEntry(_("Tuner"), nimConfig.connectedTo, _("This setting allows the tuner configuration to be a duplication of how another tuner is already configured.")))
			elif nimConfig.configMode.value == "satposdepends":
				choices = []
				nimlist = nimmanager.canDependOn(self.nim.slot)
				for id in nimlist:
					choices.append((str(id), nimmanager.getNimDescription(id)))
				nimConfig.connectedTo.setChoices(choices)
				self.list.append(getConfigListEntry(_("Tuner"), nimConfig.connectedTo, _("Select the tuner that controls the motorised dish.")))
			elif nimConfig.configMode.value == "loopthrough":
				choices = []
				print("connectable to:", nimmanager.canConnectTo(self.slotid))
				connectable = nimmanager.canConnectTo(self.slotid)
				for id in connectable:
					choices.append((str(id), nimmanager.getNimDescription(id)))
				nimConfig.connectedTo.setChoices(choices)
				self.list.append(getConfigListEntry(_("Connected to"), nimConfig.connectedTo, _("Select the tuner that this loopthrough depends on.")))
			elif nimConfig.configMode.value == "nothing":
				pass
			elif nimConfig.configMode.value == "advanced": # advanced
				# SATs
				self.advancedSatsEntry = getConfigListEntry(_("Satellite"), nimConfig.advanced.sats, _("Select the satellite you want to configure. Once that satellite is configured you can select and configure other satellites that will be accessed using this same tuner."))
				self.list.append(self.advancedSatsEntry)
				current_config_sats = nimConfig.advanced.sats.value
				if current_config_sats in ("3605", "3606"):
					self.advancedSelectSatsEntry = getConfigListEntry(_("Press OK to select satellites"), nimConfig.pressOKtoList, _("Selecting this option allows you to configure a group of satellites in one block."))
					self.list.append(self.advancedSelectSatsEntry)
					self.fillListWithAdvancedSatEntrys(nimConfig.advanced.sat[int(current_config_sats)])
				else:
					cur_orb_pos = nimConfig.advanced.sats.orbital_position
					satlist = list(nimConfig.advanced.sat.keys())
					if cur_orb_pos is not None:
						if cur_orb_pos not in satlist:
							cur_orb_pos = satlist[0]
						self.fillListWithAdvancedSatEntrys(nimConfig.advanced.sat[cur_orb_pos])
				self.have_advanced = True
			if path.exists("/proc/stb/frontend/%d/tone_amplitude" % self.nim.slot) and config.usage.setup_level.index >= 2: # expert
				self.list.append(getConfigListEntry(_("Tone amplitude"), nimConfig.toneAmplitude, _("Your receiver can use tone amplitude. Consult your receiver's manual for more information.")))
			if path.exists("/proc/stb/frontend/%d/use_scpc_optimized_search_range" % self.nim.slot) and config.usage.setup_level.index >= 2: # expert
				self.list.append(getConfigListEntry(_("SCPC optimized search range"), nimConfig.scpcSearchRange, _("Your receiver can use SCPC optimized search range. Consult your receiver's manual for more information.")))
			if path.exists("/proc/stb/frontend/%d/t2mirawmode" % self.nim.slot) and config.usage.setup_level.index >= 2: # expert
				self.list.append(getConfigListEntry(_("T2MI RAW Mode"), nimConfig.t2miRawMode, _("With T2MI RAW mode disabled (default) we can use single T2MI PLP de-encapsulation. With T2MI RAW mode enabled we can use astra-sm to analyze T2MI")))

		elif self.nim.isCompatible("DVB-C"):
			self.configMode = getConfigListEntry(_("Configuration mode"), self.nimConfig.dvbc.configMode, _("Select 'enabled' if this tuner has a signal cable connected, otherwise select 'nothing connected'."))
			self.list.append(self.configMode)
			if self.nimConfig.dvbc.configMode.value == "enabled":
				self.list.append(getConfigListEntry(_("Network ID"), self.nimConfig.dvbc.scan_networkid, _("This setting depends on your cable provider and location. If you don't know the correct setting refer to the menu in the official cable receiver, or get it from your cable provider, or seek help via internet forum.")))
				self.cableScanType = getConfigListEntry(_("Used service scan type"), self.nimConfig.dvbc.scan_type, _("Select 'provider' to scan from the predefined list of cable multiplexes. Select 'bands' to only scan certain parts of the spectrum. Select 'steps' to scan in steps of a particular frequency bandwidth."))
				self.list.append(self.cableScanType)
				if self.nimConfig.dvbc.scan_type.value == "provider":
					# country/region tier one
					if self.cableCountriesEntry is None:
						cablecountrycodelist = nimmanager.getCablesCountrycodeList()
						cablecountrycode = nimmanager.getCableCountrycode(self.slotid)
						default = cablecountrycode in cablecountrycodelist and cablecountrycode or None
						choices = [("all", _("All"))] + sorted([(x, self.countrycodeToCountry(x)) for x in cablecountrycodelist], key=lambda listItem: listItem[1])
						self.cableCountries = ConfigSelection(default=default, choices=choices)
						self.cableCountriesEntry = getConfigListEntry(_("Country"), self.cableCountries, _("Select your country. If not available select 'all'."))
						self.originalCableRegion = self.nimConfig.dvbc.scan_provider.value
					# country/region tier two
					if self.cableCountries.value == "all":
						cableNames = [x[0] for x in sorted(sorted(nimmanager.getCablesList(), key=lambda listItem: listItem[0]), key=lambda listItem: self.countrycodeToCountry(listItem[2]))]
					else:
						cableNames = sorted([x[0] for x in nimmanager.getCablesByCountrycode(self.cableCountries.value)])
					default = self.nimConfig.dvbc.scan_provider.value in cableNames and self.nimConfig.dvbc.scan_provider.value or None
					self.cableRegions = ConfigSelection(default=default, choices=cableNames)

					def updateCableProvider(configEntry):
						self.nimConfig.dvbc.scan_provider.value = configEntry.value
						self.nimConfig.dvbc.scan_provider.save()
					self.cableRegions.addNotifier(updateCableProvider)
					self.cableRegionsEntry = getConfigListEntry(_("Region"), self.cableRegions, _("Select your provider and region. If not present in this list you will need to select one of the other 'service scan types'."))
					self.list.append(self.cableCountriesEntry)
					self.list.append(self.cableRegionsEntry)
				else:
					if self.nimConfig.dvbc.scan_type.value == "bands":
						# TRANSLATORS: option name, indicating which type of (DVB-C) band should be scanned. The name of the band is printed in '%s'. E.g.: 'Scan EU MID band'
						self.list.append(getConfigListEntry(_("Scan %s band") % "EU VHF I", self.nimConfig.dvbc.scan_band_EU_VHF_I, _("Select 'yes' to include the %s band in your search.") % ("EU VHF I")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "EU MID", self.nimConfig.dvbc.scan_band_EU_MID, _("Select 'yes' to include the %s band in your search.") % ("EU MID")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "EU VHF III", self.nimConfig.dvbc.scan_band_EU_VHF_III, _("Select 'yes' to include the %s band in your search.") % ("EU VHF III")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "EU UHF IV", self.nimConfig.dvbc.scan_band_EU_UHF_IV, _("Select 'yes' to include the %s band in your search.") % ("EU VHF IV")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "EU UHF V", self.nimConfig.dvbc.scan_band_EU_UHF_V, _("Select 'yes' to include the %s band in your search.") % ("EU VHF V")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "EU SUPER", self.nimConfig.dvbc.scan_band_EU_SUPER, _("Select 'yes' to include the %s band in your search.") % ("EU SUPER")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "EU HYPER", self.nimConfig.dvbc.scan_band_EU_HYPER, _("Select 'yes' to include the %s band in your search.") % ("EU HYPER")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "US LOW", self.nimConfig.dvbc.scan_band_US_LOW, _("Select 'yes' to include the %s band in your search.") % ("US LOW")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "US MID", self.nimConfig.dvbc.scan_band_US_MID, _("Select 'yes' to include the %s band in your search.") % ("US MID")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "US HIGH", self.nimConfig.dvbc.scan_band_US_HIGH, _("Select 'yes' to include the %s band in your search.") % ("US HIGH")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "US SUPER", self.nimConfig.dvbc.scan_band_US_SUPER, _("Select 'yes' to include the %s band in your search.") % ("US SUPER")))
						self.list.append(getConfigListEntry(_("Scan %s band") % "US HYPER", self.nimConfig.dvbc.scan_band_US_HYPER, _("Select 'yes' to include the %s band in your search.") % ("US HYPER")))
					elif self.nimConfig.dvbc.scan_type.value == "steps":
						self.list.append(getConfigListEntry(_("Frequency scan step size(khz)"), self.nimConfig.dvbc.scan_frequency_steps, _("Enter the frequency step size for the tuner to use when searching for cable multiplexes. For more information consult your cable provider's documentation.")))
					# TRANSLATORS: option name, indicating which type of (DVB-C) modulation should be scanned. The modulation type is printed in '%s'. E.g.: 'Scan QAM16'
					if self.nim.description != "ATBM781x":
						self.list.append(getConfigListEntry(_("Scan %s") % "QAM16", self.nimConfig.dvbc.scan_mod_qam16, _("Select 'yes' to include %s multiplexes in your search.") % ("QAM16")))
						self.list.append(getConfigListEntry(_("Scan %s") % "QAM32", self.nimConfig.dvbc.scan_mod_qam32, _("Select 'yes' to include %s multiplexes in your search.") % ("QAM32")))
						self.list.append(getConfigListEntry(_("Scan %s") % "QAM64", self.nimConfig.dvbc.scan_mod_qam64, _("Select 'yes' to include %s multiplexes in your search.") % ("QAM64")))
						self.list.append(getConfigListEntry(_("Scan %s") % "QAM128", self.nimConfig.dvbc.scan_mod_qam128, _("Select 'yes' to include %s multiplexes in your search.") % ("QAM128")))
						self.list.append(getConfigListEntry(_("Scan %s") % "QAM256", self.nimConfig.dvbc.scan_mod_qam256, _("Select 'yes' to include %s multiplexes in your search.") % ("QAM256")))
						self.list.append(getConfigListEntry(_("Scan %s") % "SR6900", self.nimConfig.dvbc.scan_sr_6900, _("Select 'yes' to include symbol rate %s in your search.") % ("6900")))
						self.list.append(getConfigListEntry(_("Scan %s") % "SR6875", self.nimConfig.dvbc.scan_sr_6875, _("Select 'yes' to include symbol rate %s in your search.") % ("6875")))
						self.list.append(getConfigListEntry(_("Scan additional SR"), self.nimConfig.dvbc.scan_sr_ext1, _("This field allows you to search an additional symbol rate up to %s.") % ("7320")))
						self.list.append(getConfigListEntry(_("Scan additional SR"), self.nimConfig.dvbc.scan_sr_ext2, _("This field allows you to search an additional symbol rate up to %s.") % ("7320")))
			self.have_advanced = False
		elif self.nim.isCompatible("DVB-T"):
			self.configMode = getConfigListEntry(_("Configuration mode"), self.nimConfig.dvbt.configMode, _("Select 'enabled' if this tuner has a signal cable connected, otherwise select 'nothing connected'."))
			self.list.append(self.configMode)
			self.have_advanced = False
			if self.nimConfig.dvbt.configMode.value == "enabled":
				# country/region tier one
				if self.terrestrialCountriesEntry is None:
					terrestrialcountrycodelist = nimmanager.getTerrestrialsCountrycodeList()
					terrestrialcountrycode = nimmanager.getTerrestrialCountrycode(self.slotid)
					default = terrestrialcountrycode in terrestrialcountrycodelist and terrestrialcountrycode or None
					choices = [("all", _("All"))] + sorted([(x, self.countrycodeToCountry(x)) for x in terrestrialcountrycodelist], key=lambda listItem: listItem[1])
					self.terrestrialCountries = ConfigSelection(default=default, choices=choices)
					self.terrestrialCountriesEntry = getConfigListEntry(_("Country"), self.terrestrialCountries, _("Select your country. If not available select 'all'."))
					self.originalTerrestrialRegion = self.nimConfig.dvbt.terrestrial.value
				# country/region tier two
				if self.terrestrialCountries.value == "all":
					terrstrialNames = [x[0] for x in sorted(sorted(nimmanager.getTerrestrialsList(), key=lambda listItem: listItem[0]), key=lambda listItem: self.countrycodeToCountry(listItem[2]))]
				else:
					terrstrialNames = sorted([x[0] for x in nimmanager.getTerrestrialsByCountrycode(self.terrestrialCountries.value)])
				default = self.nimConfig.dvbt.terrestrial.value in terrstrialNames and self.nimConfig.dvbt.terrestrial.value or None
				self.terrestrialRegions = ConfigSelection(default=default, choices=terrstrialNames)

				def updateTerrestrialProvider(configEntry):
					self.nimConfig.dvbt.terrestrial.value = configEntry.value
					self.nimConfig.dvbt.terrestrial.save()
				self.terrestrialRegions.addNotifier(updateTerrestrialProvider)
				self.terrestrialRegionsEntry = getConfigListEntry(_("Region"), self.terrestrialRegions, _("Select your region. If not available change 'Country' to 'all' and select one of the default alternatives."))
				self.list.append(self.terrestrialCountriesEntry)
				self.list.append(self.terrestrialRegionsEntry)
				if not getBoxType() in ('spycat'):
					self.list.append(getConfigListEntry(_("Enable 5V for active antenna"), self.nimConfig.dvbt.terrestrial_5V, _("Enable this setting if your aerial system needs power")))
		elif self.nim.isCompatible("ATSC"):
			self.configMode = getConfigListEntry(_("Configuration mode"), self.nimConfig.atsc.configMode, _("Select 'enabled' if this tuner has a signal cable connected, otherwise select 'nothing connected'."))
			self.list.append(self.configMode)
			if self.nimConfig.atsc.configMode.value == "enabled":
				self.list.append(getConfigListEntry(_("ATSC provider"), self.nimConfig.atsc.atsc, _("Select your ATSC provider.")))
			self.have_advanced = False
		else:
			self.have_advanced = False

		if config.usage.setup_level.index > 1:
			self.list.append(getConfigListEntry(_("Force Legacy Signal stats"), self.nimConfig.force_legacy_signal_stats, _("If set to 'yes' signal values (SNR, etc) will be calculated from API V3. This is an old API version that has now been superseded.")))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def newConfig(self):
		self.setTextKeyBlue()
		checkList = (self.configMode, self.diseqcModeEntry, self.advancedSatsEntry,
					 self.advancedLnbsEntry, self.advancedDiseqcMode, self.advancedUsalsEntry,
					 self.advancedLof, self.advancedPowerMeasurement, self.turningSpeed,
					 self.advancedType, self.advancedSCR, self.advancedDiction, self.advancedManufacturer, self.advancedUnicable, self.advancedConnected, self.advancedUnicableTuningAlgo,
					 self.toneburst, self.committedDiseqcCommand, self.uncommittedDiseqcCommand, self.singleSatEntry,
					 self.commandOrder, self.showAdditionalMotorOptions, self.cableScanType, self.terrestrialCountriesEntry, self.cableCountriesEntry, self.multiType)
		if self["config"].getCurrent() == self.multiType and self.multiType:
			update_slots = [self.slotid]
			from Components.NimManager import InitNimManager
			InitNimManager(nimmanager, update_slots)
			self.nim = nimmanager.nim_slots[self.slotid]
			self.nimConfig = self.nim.config

		for x in checkList:
			if self["config"].getCurrent() == x and x:
				self.createSetup()
				break

	def run(self):
		if self.nim.canBeCompatible("DVB-S"):
			if self.nimConfig.dvbs.configMode.value == "simple":
				autodiseqc_ports = 0
				if self.nimConfig.dvbs.diseqcMode.value == "single":
					if self.nimConfig.dvbs.diseqcA.orbital_position == 3600:
						autodiseqc_ports = 1
				elif self.nimConfig.dvbs.diseqcMode.value == "diseqc_a_b":
					if self.nimConfig.dvbs.diseqcA.orbital_position == 3600 or self.nimConfig.dvbs.diseqcB.orbital_position == 3600:
						autodiseqc_ports = 2
				elif self.nimConfig.dvbs.diseqcMode.value == "diseqc_a_b_c_d":
					if self.nimConfig.dvbs.diseqcA.orbital_position == 3600 or self.nimConfig.dvbs.diseqcB.orbital_position == 3600 or self.nimConfig.dvbs.diseqcC.orbital_position == 3600 or self.nimConfig.dvbs.diseqcD.orbital_position == 3600:
						autodiseqc_ports = 4
				if autodiseqc_ports:
					self.autoDiseqcRun(autodiseqc_ports)
					return False
			if self.have_advanced and self.nimConfig.dvbs.configMode.value == "advanced":
				# fillAdvancedList resets self.list so some entries like t2mirawmode removed
				# saveAll will save any unsaved data before self.list entries are gone
				self.saveAll()
				self.fillAdvancedList()
		for x in self.list:
			if x in (self.turnFastEpochBegin, self.turnFastEpochEnd):
				# workaround for storing only hour*3600+min*60 value in configfile
				# not really needed.. just for cosmetics..
				tm = localtime(x[1].value)
				dt = datetime(1970, 1, 1, tm.tm_hour, tm.tm_min)
				x[1].value = int(mktime(dt.timetuple()))
			x[1].save()
		nimmanager.sec.update()
		self.saveAll()
		return True

	def autoDiseqcRun(self, ports):
		self.session.openWithCallback(self.autoDiseqcCallback, AutoDiseqc, self.slotid, ports, self.nimConfig.dvbs.simpleDiSEqCSetVoltageTone, self.nimConfig.dvbs.simpleDiSEqCOnlyOnSatChange)

	def autoDiseqcCallback(self, result):
		from Screens.Wizard import Wizard
		if Wizard.instance is not None:
			Wizard.instance.back()
		else:
			self.createSetup()

	def fillListWithAdvancedSatEntrys(self, Sat):
		lnbnum = int(Sat.lnb.value)
		nimConfig_advanced = self.nimConfig.dvbs.advanced
		currLnb = nimConfig_advanced.lnb[lnbnum]
		diction = None
		if isinstance(currLnb, ConfigNothing):
			currLnb = None

		# LNBs
		self.advancedLnbsEntry = getConfigListEntry(_("LNB"), Sat.lnb, _("Allocate a number to the physical LNB you are configuring. You will be able to select this LNB again for other satellites (e.g. motorised dishes) to save setting up the same LNB multiple times."))
		self.list.append(self.advancedLnbsEntry)

		if currLnb:
			if isFBCLink(self.nim.slot):
				if currLnb.lof.value != "unicable":
					currLnb.lof.value = "unicable"
			self.list.append(getConfigListEntry(_("Priority"), currLnb.prio, _("This setting is for special setups only. It gives this LNB higher priority over other LNBs with lower values. The free LNB with the highest priority will be the first LNB selected for tuning services.")))
			self.advancedLof = getConfigListEntry(_("LOF"), currLnb.lof, _("Select the type of LNB/device being used (normally 'Universal'). If your LNB type is not available select 'user defined'."))
			self.list.append(self.advancedLof)
			if currLnb.lof.value == "user_defined":
				self.list.append(getConfigListEntry(_("LOF/L"), currLnb.lofl, _("Enter your low band local oscillator frequency. For more information consult the spec sheet of your LNB.")))
				self.list.append(getConfigListEntry(_("LOF/H"), currLnb.lofh, _("Enter your high band local oscillator frequency. For more information consult the spec sheet of your LNB.")))
				self.list.append(getConfigListEntry(_("Threshold"), currLnb.threshold, _("Enter the frequency at which you LNB switches between low band and high band. For more information consult the spec sheet of your LNB.")))

			if currLnb.lof.value == "unicable":
				self.advancedUnicable = getConfigListEntry(_("Unicable ") + _("Configuration mode"), currLnb.unicable, _("Select the type of Single Cable Reception device you are using."))
				self.list.append(self.advancedUnicable)
				if currLnb.unicable.value == "unicable_user":
					self.advancedDiction = getConfigListEntry(_("Diction"), currLnb.dictionuser, _("Select the protocol used by your SCR device. Choices are 'SCR Unicable' (Unicable), or 'SCR JESS' (JESS, also known as Unicable II)."))
					self.list.append(self.advancedDiction)
					if currLnb.dictionuser.value == "EN50494":
						satcr = currLnb.satcruserEN50494
						stcrvco = currLnb.satcrvcouserEN50494[currLnb.satcruserEN50494.index]
					elif currLnb.dictionuser.value == "EN50607":
						satcr = currLnb.satcruserEN50607
						stcrvco = currLnb.satcrvcouserEN50607[currLnb.satcruserEN50607.index]
					self.advancedSCR = getConfigListEntry(_("Channel"), satcr, _("Select the Unicable channel to be assigned to this tuner. This is a unique value. Be certain that no other device connected to this same Unicable system is allocated to the same Unicable channel."))
					self.list.append(self.advancedSCR)
					self.list.append(getConfigListEntry(_("Frequency"), stcrvco, _("Select the User Band frequency to be assigned to this tuner. This is the frequency the SCR switch or SCR LNB uses to pass the requested transponder to the tuner.")))
					self.list.append(getConfigListEntry(_("LOF/L"), currLnb.lofl, _("Consult your SCR device spec sheet for this information.")))
					self.list.append(getConfigListEntry(_("LOF/H"), currLnb.lofh, _("Consult your SCR device spec sheet for this information.")))
					self.list.append(getConfigListEntry(_("Threshold"), currLnb.threshold, _("Consult your SCR device spec sheet for this information.")))
					self.list.append(getConfigListEntry(_("LNB/Switch Bootup time [ms]"), currLnb.bootuptimeuser))
				elif currLnb.unicable.value == "unicable_matrix":
					nimmanager.sec.reconstructUnicableDate(currLnb.unicableMatrixManufacturer, currLnb.unicableMatrix, currLnb)
					manufacturer_name = six.ensure_text(currLnb.unicableMatrixManufacturer.value)
					manufacturer = currLnb.unicableMatrix[manufacturer_name]
					product_name = six.ensure_text(manufacturer.product.value)
					self.advancedManufacturer = getConfigListEntry(_("Manufacturer"), currLnb.unicableMatrixManufacturer, _("Select the manufacturer of your SCR device. If the manufacturer is not listed, set 'SCR' to 'user defined' and enter the device parameters manually according to its spec sheet."))
					self.list.append(self.advancedManufacturer)
					if product_name in manufacturer.scr:
						diction = manufacturer.diction[product_name].value
						self.advancedType = getConfigListEntry(_("Type"), manufacturer.product, _("Select the model number of your Unicable device. If the model number is not listed, set 'SCR' to 'user defined' and enter the device parameters manually according to its spec sheet."))
						self.advancedSCR = getConfigListEntry(_("Channel"), manufacturer.scr[product_name], _("Select the User Band channel to be assigned to this tuner. This is an index into the table of frequencies the SCR switch uses to pass the requested transponder to the tuner."))
						self.list.append(self.advancedType)
						self.list.append(self.advancedSCR)
						self.list.append(getConfigListEntry(_("Frequency"), manufacturer.vco[product_name][manufacturer.scr[product_name].index], _("Select the User Band frequency to be assigned to this tuner. This is the frequency the SCR switch uses to pass the requested transponder to the tuner.")))
				elif currLnb.unicable.value == "unicable_lnb":
					nimmanager.sec.reconstructUnicableDate(currLnb.unicableLnbManufacturer, currLnb.unicableLnb, currLnb)
					manufacturer_name = six.ensure_text(currLnb.unicableLnbManufacturer.value)
					manufacturer = currLnb.unicableLnb[manufacturer_name]
					product_name = six.ensure_text(manufacturer.product.value)
					self.advancedManufacturer = getConfigListEntry(_("Manufacturer"), currLnb.unicableLnbManufacturer, _("Select the manufacturer of your SCR device. If the manufacturer is not listed, set 'SCR' to 'user defined' and enter the device parameters manually according to its spec sheet."))
					self.list.append(self.advancedManufacturer)
					if product_name in manufacturer.scr:
						diction = manufacturer.diction[product_name].value
						self.advancedType = getConfigListEntry(_("Type"), manufacturer.product, _("Select the model number of your Unicable device. If the model number is not listed, set 'SCR' to 'user defined' and enter the device parameters manually according to its spec sheet."))
						self.advancedSCR = getConfigListEntry(_("Channel"), manufacturer.scr[product_name], _("Select the User Band channel to be assigned to this tuner. This is an index into the table of frequencies the SCR LNB uses to pass the requested transponder to the tuner."))
						self.list.append(self.advancedType)
						self.list.append(self.advancedSCR)
						self.list.append(getConfigListEntry(_("Frequency"), manufacturer.vco[product_name][manufacturer.scr[product_name].index], _("Select the User Band frequency to be assigned to this tuner. This is the frequency the SCR LNB uses to pass the requested transponder to the tuner.")))

				self.advancedUnicableTuningAlgo = getConfigListEntry(_("Tuning algorithm"), currLnb.unicableTuningAlgo, _("SCR timing adjustment, in conjunction with SCR socket and operation of several SCR devices with one cable."))
				self.list.append(self.advancedUnicableTuningAlgo)

				choices = []
				connectable = nimmanager.canConnectTo(self.slotid)
				for id in connectable:
					choices.append((str(id), nimmanager.getNimDescription(id)))
				if len(choices):
					if isFBCLink(self.nim.slot):
						if nimConfig_advanced.unicableconnected.value != True:
							nimConfig_advanced.unicableconnected.value = True
					self.advancedConnected = getConfigListEntry(_("connected"), nimConfig_advanced.unicableconnected, _("Select 'yes' if this tuner is connected to the SCR device through another tuner, otherwise select 'no'."))
					self.list.append(self.advancedConnected)
					if nimConfig_advanced.unicableconnected.value:
						nimConfig_advanced.unicableconnectedTo.setChoices(choices)
						self.list.append(getConfigListEntry(_("Connected to"), nimConfig_advanced.unicableconnectedTo, _("Select the tuner to which the signal cable of the SCR device is connected.")))

			else:	#no Unicable
				self.list.append(getConfigListEntry(_("Voltage mode"), Sat.voltage, _("Select 'polarisation' if using a 'universal' LNB, otherwise consult your LNB spec sheet.")))
				self.list.append(getConfigListEntry(_("Tone mode"), Sat.tonemode, _("Select 'band' if using a 'universal' LNB, otherwise consult your LNB spec sheet.")))
			self.list.append(getConfigListEntry(_("Increased voltage"), currLnb.increased_voltage, _("use increased voltage '14/18V' if there are problems when switching the lnb")))

			if lnbnum < 65 and diction != "EN50607":
				self.advancedDiseqcMode = getConfigListEntry(_("DiSEqC mode"), currLnb.diseqcMode, _("Select '1.0' for standard committed switches, '1.1' for uncommitted switches, and '1.2' for systems using a positioner."))
				self.list.append(self.advancedDiseqcMode)
			if currLnb.diseqcMode.value != "none":
				self.list.append(getConfigListEntry(_("Fast DiSEqC"), currLnb.fastDiseqc, _("Select Fast DiSEqC if your aerial system supports this. If you are unsure select 'no'.")))
				self.toneburst = getConfigListEntry(_("Toneburst"), currLnb.toneburst, _("Select 'A' or 'B' if your aerial system requires this, otherwise select 'none'. If you are unsure select 'none'."))
				self.list.append(self.toneburst)
				self.committedDiseqcCommand = getConfigListEntry(_("DiSEqC 1.0 command"), currLnb.commitedDiseqcCommand, _("If you are using a DiSEqC committed switch enter the port letter required to access the LNB used for this satellite."))
				self.list.append(self.committedDiseqcCommand)

				if currLnb.diseqcMode.value == "1_0":
					if currLnb.toneburst.index and currLnb.commitedDiseqcCommand.index:
						self.list.append(getConfigListEntry(_("Command order"), currLnb.commandOrder1_0, _("This is the order in which DiSEqC commands are sent to the aerial system. The order must correspond exactly with the order the physical devices are arranged along the signal cable (starting from the receiver end).")))
				else:
					self.uncommittedDiseqcCommand = getConfigListEntry(_("DiSEqC 1.1 command"), currLnb.uncommittedDiseqcCommand, _("If you are using a DiSEqC uncommitted switch enter the port number required to access the LNB used for this satellite."))
					self.list.append(self.uncommittedDiseqcCommand)
					if currLnb.uncommittedDiseqcCommand.index:
						if currLnb.commandOrder.value == "ct":
							currLnb.commandOrder.value = "cut"
						elif currLnb.commandOrder.value == "tc":
							currLnb.commandOrder.value = "tcu"
					else:
						if currLnb.commandOrder.index & 1:
							currLnb.commandOrder.value = "tc"
						else:
							currLnb.commandOrder.value = "ct"
					self.commandOrder = getConfigListEntry(_("Command order"), currLnb.commandOrder, _("This is the order in which DiSEqC commands are sent to the aerial system. The order must correspond exactly with the order the physical devices are arranged along the signal cable (starting from the receiver end)."))
					if 1 < ((1 if currLnb.uncommittedDiseqcCommand.index else 0) + (1 if currLnb.commitedDiseqcCommand.index else 0) + (1 if currLnb.toneburst.index else 0)):
						self.list.append(self.commandOrder)
					if currLnb.uncommittedDiseqcCommand.index:
						self.list.append(getConfigListEntry(_("DiSEqC 1.1 repeats"), currLnb.diseqcRepeats, _("If using multiple uncommitted switches the DiSEqC commands must be sent multiple times. Set to the number of uncommitted switches in the chain minus one.")))
				self.list.append(getConfigListEntry(_("Sequence repeat"), currLnb.sequenceRepeat, _("Set sequence repeats if your aerial system requires this. Normally if the aerial system has been configured correctly sequence repeats will not be necessary. If yours does, recheck you have command order set correctly.")))
				if currLnb.diseqcMode.value == "1_2":
					if SystemInfo["CanMeasureFrontendInputPower"]:
						self.advancedPowerMeasurement = getConfigListEntry(_("Use power measurement"), currLnb.powerMeasurement, _("Power management. Consult your receiver's manual for more information."))
						self.list.append(self.advancedPowerMeasurement)
						if currLnb.powerMeasurement.value:
							self.list.append(getConfigListEntry(_("Power threshold in mA"), currLnb.powerThreshold, _("Power threshold. Consult your receiver's manual for more information.")))
							self.turningSpeed = getConfigListEntry(_("Rotor turning speed"), currLnb.turningSpeed, _("Select how quickly the dish should move between satellites."))
							self.list.append(self.turningSpeed)
							if currLnb.turningSpeed.value == "fast epoch":
								self.turnFastEpochBegin = getConfigListEntry(_("Begin time"), currLnb.fastTurningBegin, _("Only move the dish quickly after this hour."))
								self.turnFastEpochEnd = getConfigListEntry(_("End time"), currLnb.fastTurningEnd, _("Only move the dish quickly before this hour."))
								self.list.append(self.turnFastEpochBegin)
								self.list.append(self.turnFastEpochEnd)
					else:
						if currLnb.powerMeasurement.value:
							currLnb.powerMeasurement.value = False
							currLnb.powerMeasurement.save()
					self.advancedUsalsEntry = getConfigListEntry(_("Use USALS for this sat"), Sat.usals, _("USALS automatically moves a motorised dish to the correct satellite based on the coordinates entered by the user. Without USALS each satellite will need to be setup and saved individually."))
					if lnbnum < 65:
						self.list.append(self.advancedUsalsEntry)
					if Sat.usals.value:
						self.list.append(getConfigListEntry(_("Longitude"), currLnb.longitude, _("Enter your current longitude. This is the number of degrees you are from zero meridian as a decimal.")))
						self.list.append(getConfigListEntry(" ", currLnb.longitudeOrientation, _("Enter if you are in the east or west hemisphere.")))
						self.list.append(getConfigListEntry(_("Latitude"), currLnb.latitude, _("Enter your current latitude. This is the number of degrees you are from the equator as a decimal.")))
						self.list.append(getConfigListEntry(" ", currLnb.latitudeOrientation, _("Enter if you are north or south of the equator.")))
					else:
						self.list.append(getConfigListEntry(_("Stored position"), Sat.rotorposition, _("Enter the number stored in the positioner that corresponds to this satellite.")))
					if not hasattr(self, 'additionalMotorOptions'):
						self.additionalMotorOptions = ConfigYesNo(False)
					self.showAdditionalMotorOptions = getConfigListEntry(_("Extra motor options"), self.additionalMotorOptions, _("Additional motor options allow you to enter details from your motor's spec sheet so enigma can work out how long it will take to move to another satellite."))
					self.list.append(self.showAdditionalMotorOptions)
					if self.additionalMotorOptions.value:
						self.list.append(getConfigListEntry("   " + _("Horizontal turning speed") + " [" + chr(176) + "/sec]", currLnb.turningspeedH, _("Consult your motor's spec sheet for this information, or leave the default setting.")))
						self.list.append(getConfigListEntry("   " + _("Vertical turning speed") + " [" + chr(176) + "/sec]", currLnb.turningspeedV, _("Consult your motor's spec sheet for this information, or leave the default setting.")))
						self.list.append(getConfigListEntry("   " + _("Turning step size") + " [" + chr(176) + "]", currLnb.tuningstepsize, _("Consult your motor's spec sheet for this information, or leave the default setting.")))
						self.list.append(getConfigListEntry("   " + _("Max memory positions"), currLnb.rotorPositions, _("Consult your motor's spec sheet for this information, or leave the default setting.")))

	def fillAdvancedList(self):
		self.list = []
		self.configMode = getConfigListEntry(_("Configuration mode"), self.nimConfig.dvbs.configMode)
		self.list.append(self.configMode)
		self.advancedSatsEntry = getConfigListEntry(_("Satellite"), self.nimConfig.dvbs.advanced.sats)
		self.list.append(self.advancedSatsEntry)
		for x in list(self.nimConfig.dvbs.advanced.sat.keys()):
			Sat = self.nimConfig.dvbs.advanced.sat[x]
			self.fillListWithAdvancedSatEntrys(Sat)
		self["config"].list = self.list

	def unicableconnection(self):
		if self.nimConfig.dvbs.configMode.value == "advanced":
			connect_count = 0
			dvbs_slots = nimmanager.getNimListOfType('DVB-S')
			dvbs_slots_len = len(dvbs_slots)

			for x in dvbs_slots:
				try:
					nim_slot = nimmanager.nim_slots[x]
					if nim_slot == self.nimConfig:
						self_idx = x
					if nim_slot.config.dvbs.configMode.value == "advanced":
						if nim_slot.config.dvbs.advanced.unicableconnected.value == True:
							connect_count += 1
				except:
					pass
			if connect_count >= dvbs_slots_len:
				return False

		self.slot_dest_list = []

		def checkRecursiveConnect(slot_id):
			if slot_id in self.slot_dest_list:
				print(slot_id)
				return False
			self.slot_dest_list.append(slot_id)
			slot_config = nimmanager.nim_slots[slot_id].config.dvbs
			if slot_config.configMode.value == "advanced":
				try:
					connected = slot_config.advanced.unicableconnected.value
				except:
					connected = False
				if connected == True:
					return checkRecursiveConnect(int(slot_config.advanced.unicableconnectedTo.value))
			return True

		return checkRecursiveConnect(self.slotid)

	def checkLoopthrough(self):
		if self.nimConfig.dvbs.configMode.value == "loopthrough":
			loopthrough_count = 0
			dvbs_slots = nimmanager.getNimListOfType('DVB-S')
			dvbs_slots_len = len(dvbs_slots)

			for x in dvbs_slots:
				try:
					nim_slot = nimmanager.nim_slots[x]
					if nim_slot == self.nimConfig:
						self_idx = x
					if nim_slot.config.dvbs.configMode.value == "loopthrough":
						loopthrough_count += 1
				except:
					pass
			if loopthrough_count >= dvbs_slots_len:
				return False

		self.slot_dest_list = []

		def checkRecursiveConnect(slot_id):
			if slot_id in self.slot_dest_list:
				return False
			self.slot_dest_list.append(slot_id)
			slot_config = nimmanager.nim_slots[slot_id].config.dvbs
			if slot_config.configMode.value == "loopthrough":
				return checkRecursiveConnect(int(slot_config.connectedTo.value))
			return True

		return checkRecursiveConnect(self.slotid)

	def keyOk(self):
		if self["config"].getCurrent() == self.advancedSelectSatsEntry and self.advancedSelectSatsEntry:
			conf = self.nimConfig.dvbs.advanced.sat[int(self.nimConfig.dvbs.advanced.sats.value)].userSatellitesList
			self.session.openWithCallback(boundFunction(self.updateConfUserSatellitesList, conf), SelectSatsEntryScreen, userSatlist=conf.value)
		elif self["config"].getCurrent() == self.selectSatsEntry and self.selectSatsEntry:
			conf = self.nimConfig.dvbs.userSatellitesList
			self.session.openWithCallback(boundFunction(self.updateConfUserSatellitesList, conf), SelectSatsEntryScreen, userSatlist=conf.value)
		else:
			self.keySave()

	def updateConfUserSatellitesList(self, conf, val=None):
		if val is not None:
			conf.value = val
			conf.save()

	def keySave(self):
		if self.nim.canBeCompatible("DVB-S"):
			if not self.unicableconnection():
				self.session.open(MessageBox, _("The unicable connection setting is wrong.\n Maybe recursive connection of tuners."), MessageBox.TYPE_ERROR, timeout=10)
				return
			if not self.checkLoopthrough():
				self.session.open(MessageBox, _("The loopthrough setting is wrong."), MessageBox.TYPE_ERROR, timeout=10)
				return

		old_configured_sats = nimmanager.getConfiguredSats()
		if not self.run():
			return
		new_configured_sats = nimmanager.getConfiguredSats()
		self.unconfed_sats = old_configured_sats - new_configured_sats
		self.satpos_to_remove = None
		self.deleteConfirmed((None, "no"))

	def deleteConfirmed(self, confirmed):
		if confirmed is None:
			confirmed = (None, "no")

		if confirmed[1] == "yes" or confirmed[1] == "yestoall":
			eDVBDB.getInstance().removeServices(-1, -1, -1, self.satpos_to_remove)

		try:
			if self.satpos_to_remove is not None:
				self.unconfed_sats.remove(self.satpos_to_remove)
		except:
			self.unconfed_sats = None

		self.satpos_to_remove = None
		for orbpos in self.unconfed_sats:
			self.satpos_to_remove = orbpos
			orbpos = self.satpos_to_remove
			try:
				# why we need this cast?
				sat_name = str(nimmanager.getSatDescription(orbpos))
			except:
				if orbpos > 1800: # west
					orbpos = 3600 - orbpos
					h = _("W")
				else:
					h = _("E")
				sat_name = ("%d.%d" + h) % (orbpos // 10, orbpos % 10)

			if confirmed[1] == "yes" or confirmed[1] == "no":
				# TRANSLATORS: The satellite with name '%s' is no longer used after a configuration change. The user is asked whether or not the satellite should be deleted.
				self.session.openWithCallback(self.deleteConfirmed, ChoiceBox, _("%s is no longer used. Should it be deleted?") % sat_name, [(_("Yes"), "yes"), (_("No"), "no"), (_("Yes to all"), "yestoall"), (_("No to all"), "notoall")], None, 1)
			if confirmed[1] == "yestoall" or confirmed[1] == "notoall":
				self.deleteConfirmed(confirmed)
			break
		else:
			self.restoreService(_("Zap back to service before tuner setup?"))

	def __init__(self, session, slotid):
		printCallSequence(10)
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Tuner settings"))
		self.setup_title = _("Tuner settings")
		self.list = []
		ServiceStopScreen.__init__(self)
		self.stopService()
		ConfigListScreen.__init__(self, self.list, on_change=self.changedEntry)

		self["key_red"] = Label(_("Close"))
		self["key_green"] = Label(_("Save"))
		self["key_yellow"] = Label(_("Configuration mode"))
		self["key_blue"] = Label()
		self["description"] = Label(" ")

		self["actions"] = ActionMap(["SetupActions", "SatlistShortcutAction", "ColorActions"],
		{
			"ok": self.keyOk,
			"save": self.keySave,
			"cancel": self.keyCancel,
			"changetype": self.changeConfigurationMode,
			"nothingconnected": self.nothingConnectedShortcut,
			"red": self.keyCancel,
			"green": self.keySave,
		}, -2)

		self.configMode = None

		self.slotid = slotid
		self.nim = nimmanager.nim_slots[slotid]
		self.nimConfig = self.nim.config
		self.createConfigMode()
		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.newConfig()
		self.setTitle(_("Reception Settings") + " " + _("Tuner") + " " + self.nim.slot_input_name)

		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def selectionChanged(self):
		self["description"].setText(self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or "")

	def keyLeft(self):
		cur = self["config"].getCurrent()
		if cur and isFBCLink(self.nim.slot):
			checkList = (self.advancedLof, self.advancedConnected)
			if cur in checkList:
				return
		ConfigListScreen.keyLeft(self)
		if cur in (self.advancedSelectSatsEntry, self.selectSatsEntry) and cur:
			self.keyOk()
		else:
			if cur == self.multiType and cur:
				self.saveAll()
			self.newConfig()

	def setTextKeyBlue(self):
		self["key_blue"].setText("")
		if self["config"].isChanged():
			self["key_blue"].setText(_("Set default"))

	def keyRight(self):
		cur = self["config"].getCurrent()
		if cur and isFBCLink(self.nim.slot):
			checkList = (self.advancedLof, self.advancedConnected)
			if cur in checkList:
				return
		ConfigListScreen.keyRight(self)
		if cur in (self.advancedSelectSatsEntry, self.selectSatsEntry) and cur:
			self.keyOk()
		else:
			if cur == self.multiType and cur:
				self.saveAll()
			self.newConfig()

	def handleKeyFileCallback(self, answer):
		ConfigListScreen.handleKeyFileCallback(self, answer)
		self.newConfig()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), default=False)
		else:
			self.restoreService(_("Zap back to service before tuner setup?"))

	def saveAll(self):
		if self.nim.isCompatible("DVB-S"):
			# reset connectedTo to all choices to properly store the default value
			choices = []
			nimlist = nimmanager.getNimListOfType("DVB-S", self.slotid)
			for id in nimlist:
				choices.append((str(id), nimmanager.getNimDescription(id)))
			self.nimConfig.dvbs.connectedTo.setChoices(choices)
			# sanity check for empty sat list
			if self.nimConfig.dvbs.configMode.value != "satposdepends" and len(nimmanager.getSatListForNim(self.slotid)) < 1:
				self.nimConfig.dvbs.configMode.value = "nothing"
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	def cancelConfirm(self, result):
		if not result:
			return

		for x in self["config"].list:
			x[1].cancel()
		if hasattr(self, "originalTerrestrialRegion"):
			self.nimConfig.dvbt.terrestrial.value = self.originalTerrestrialRegion
			self.nimConfig.dvbt.terrestrial.save()
		if hasattr(self, "originalCableRegion"):
			self.nimConfig.dvbc.scan_provider.value = self.originalCableRegion
			self.nimConfig.dvbc.scan_provider.save()
		# we need to call saveAll to reset the connectedTo choices
		self.saveAll()
		self.restoreService(_("Zap back to service before tuner setup?"))

	def changeConfigurationMode(self):
		if self.configMode:
			if self.nim.isCompatible("DVB-S"):
				self.nimConfig.dvbs.configMode.selectNext()
			elif self.nim.isCompatible("DVB-C"):
				self.nimConfig.dvbc.configMode.selectNext()
			elif self.nim.isCompatible("DVB-T"):
				self.nimConfig.dvbt.configMode.selectNext()
			else:
				pass
			self["config"].invalidate(self.configMode)
			self.setTextKeyBlue()
			self.createSetup()

	def nothingConnectedShortcut(self):
		if self["config"].isChanged():
			for x in self["config"].list:
				x[1].cancel()
			self.setTextKeyBlue()
			self.createSetup()

	def countrycodeToCountry(self, cc):
		if not hasattr(self, 'countrycodes'):
			self.countrycodes = {}
			from Tools.CountryCodes import ISO3166
			for country in ISO3166:
				self.countrycodes[country[2]] = country[0]
		if cc.upper() in self.countrycodes:
			return self.countrycodes[cc.upper()]
		return cc

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary


class NimSelection(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Tuner configuration"))

		self.list = [None] * nimmanager.getSlotCount()
		self["nimlist"] = List(self.list)
		self.loadFBCLinks()
		self.updateList()

		self.setResultClass()

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Select"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "MenuActions", "ChannelSelectEPGActions"],
		{
			"ok": self.okbuttonClick,
			"info": self.extraInfo,
			"epg": self.extraInfo,
			"cancel": self.close,
			"red": self.close,
			"green": self.okbuttonClick,
			"menu": self.exit,
		}, -2)
		self.setTitle(_("Choose Tuner"))

	def loadFBCLinks(self):
		for x in nimmanager.nim_slots:
			slotid = x.slot
			if self.showNim(x):
				if x.isCompatible("DVB-S"):
					nimConfig = nimmanager.getNimConfig(x.slot).dvbs
					configMode = nimConfig.configMode.value
					if isFBCLink(x.slot) and configMode != "advanced":
						link = getLinkedSlotID(x.slot)

						if link == -1:
							nimConfig.configMode.value = "nothing"
						else:
							nimConfig.configMode.value = "loopthrough"
							nimConfig.connectedTo.value = str(link)

	def exit(self):
		self.close(True)

	def setResultClass(self):
		self.resultclass = NimSetup

	def extraInfo(self):
		nim = self["nimlist"].getCurrent()
		nim = nim and nim[3]
		if config.usage.setup_level.index >= 2 and nim is not None:
			text = _("Capabilities: ") + ",".join(eDVBResourceManager.getInstance().getFrontendCapabilities(nim.slot).splitlines())
			self.session.open(MessageBox, text, MessageBox.TYPE_INFO, simple=True)

	def okbuttonClick(self):
		nim = self["nimlist"].getCurrent()
		nim = nim and nim[3]

		if isFBCLink(nim.slot):
			if nim.isCompatible("DVB-S"):
				nimConfig = nimmanager.getNimConfig(nim.slot).dvbs
			elif nim.isCompatible("DVB-C"):
				nimConfig = nimmanager.getNimConfig(nim.slot).dvbc
			elif nim.isCompatible("DVB-T"):
				nimConfig = nimmanager.getNimConfig(nim.slot).dvbt

			if nimConfig.configMode.value == "loopthrough":
				return
		if nim is not None and not nim.empty and nim.isSupported():
			self.session.openWithCallback(boundFunction(self.NimSetupCB, self["nimlist"].getIndex()), self.resultclass, nim.slot)

	def NimSetupCB(self, index=None):
		self.loadFBCLinks()
		self.updateList(index)

	def showNim(self, nim):
		return True

	def updateList(self, index=None):
		self.list = []
		for x in nimmanager.nim_slots:
			slotid = x.slot
			text = ""
			if self.showNim(x):
				if x.isMultiType():
					if x.canBeCompatible("DVB-S") and nimmanager.getNimConfig(x.slot).dvbs.configMode.value != "nothing":
						text = " DVB-S,"
					if x.canBeCompatible("DVB-C") and nimmanager.getNimConfig(x.slot).dvbc.configMode.value != "nothing":
						text = " DVB-C," + text
					if x.canBeCompatible("DVB-T") and nimmanager.getNimConfig(x.slot).dvbt.configMode.value != "nothing":
						text = " DVB-T," + text
					if text:
						text = _("Enabled") + ":" + text[:-1]
					else:
						text = _("nothing connected")
					text = _("Switchable tuner types:") + "(" + ','.join(list(x.getMultiTypeList().values())) + ")" + "\n" + text
				elif x.isCompatible("DVB-S"):
					nimConfig = nimmanager.getNimConfig(x.slot).dvbs
					text = nimConfig.configMode.value
					if nimConfig.configMode.value in ("loopthrough", "equal", "satposdepends"):
						text = {"loopthrough": _("Loop through to"),
								 "equal": _("Equal to"),
								 "satposdepends": _("Second cable of motorized LNB")}[nimConfig.configMode.value]
						if len(x.input_name) > 1:
							text += " " + _("Tuner") + " " + ["A1", "A2", "B", "C"][int(nimConfig.connectedTo.value)]
						else:
							text += " " + _("Tuner") + " " + chr(ord('A') + int(nimConfig.connectedTo.value))
					elif nimConfig.configMode.value == "nothing":
						text = _("not configured")
					elif nimConfig.configMode.value == "simple":
						if nimConfig.diseqcMode.value in ("single", "toneburst_a_b", "diseqc_a_b", "diseqc_a_b_c_d"):
							text = {"single": _("Single"), "toneburst_a_b": _("Toneburst A/B"), "diseqc_a_b": _("DiSEqC A/B"), "diseqc_a_b_c_d": _("DiSEqC A/B/C/D")}[nimConfig.diseqcMode.value] + "\n"
							text += _("Sats") + ": "
							satnames = []
							if nimConfig.diseqcA.orbital_position < 3600:
								satnames.append(nimmanager.getSatName(int(nimConfig.diseqcA.value)))
							if nimConfig.diseqcMode.value in ("toneburst_a_b", "diseqc_a_b", "diseqc_a_b_c_d"):
								if nimConfig.diseqcB.orbital_position < 3600:
									satnames.append(nimmanager.getSatName(int(nimConfig.diseqcB.value)))
							if nimConfig.diseqcMode.value == "diseqc_a_b_c_d":
								if nimConfig.diseqcC.orbital_position < 3600:
									satnames.append(nimmanager.getSatName(int(nimConfig.diseqcC.value)))
								if nimConfig.diseqcD.orbital_position < 3600:
									satnames.append(nimmanager.getSatName(int(nimConfig.diseqcD.value)))
							if len(satnames) <= 2:
								text += ", ".join(satnames)
							elif len(satnames) > 2:
								# we need a newline here, since multi content lists don't support automtic line wrapping
								text += ", ".join(satnames[:2]) + ",\n"
								text += "         " + ", ".join(satnames[2:])
						elif nimConfig.diseqcMode.value in ("positioner", "positioner_select"):
							text = {"positioner": _("Positioner"), "positioner_select": _("Positioner (selecting satellites)")}[nimConfig.diseqcMode.value]
							text += ":"
							if nimConfig.positionerMode.value == "usals":
								text += "USALS"
							elif nimConfig.positionerMode.value == "manual":
								text += _("Manual")
						else:
							text = _("Simple")
					elif nimConfig.configMode.value == "advanced":
						text = _("Advanced")
					if isFBCLink(x.slot) and nimConfig.configMode.value != "advanced":
						text += _("\n<This tuner is configured automatically>")
				elif x.isCompatible("DVB-T"):
					nimConfig = nimmanager.getNimConfig(x.slot).dvbt
					if nimConfig.configMode.value == "nothing":
						text = _("nothing connected")
					elif nimConfig.configMode.value == "enabled":
						text = _("Enabled")
				elif x.isCompatible("DVB-C"):
					nimConfig = nimmanager.getNimConfig(x.slot).dvbc
					if nimConfig.configMode.value == "nothing":
						text = _("nothing connected")
					elif nimConfig.configMode.value == "enabled":
						text = _("Enabled")
				elif x.isCompatible("ATSC"):
					nimConfig = nimmanager.getNimConfig(x.slot).atsc
					if nimConfig.configMode.value == "nothing":
						text = _("nothing connected")
					elif nimConfig.configMode.value == "enabled":
						text = _("Enabled")
				if not x.isSupported():
					text = _("Tuner is not supported")

				self.list.append((slotid, x.friendly_full_description, text, x))
		self["nimlist"].setList(self.list)
		self["nimlist"].updateList(self.list)
		if index is not None:
			self["nimlist"].setIndex(index)


class SelectSatsEntryScreen(Screen):
	skin = """
		<screen name="SelectSatsEntryScreen" position="center,center" size="560,410" title="Select Sats Entry" >
			<ePixmap name="red" position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="list" position="10,40" size="540,330" scrollbarMode="showNever" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,375" zPosition="1" size="540,2" transparent="1" alphatest="on" />
			<widget name="hint" position="10,380" size="540,25" font="Regular;19" halign="center" transparent="1" />
		</screen>"""

	def __init__(self, session, userSatlist=[]):
		Screen.__init__(self, session)
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save"))
		self["key_yellow"] = Button(_("Sort by"))
		self["key_blue"] = Button(_("Select all"))
		self["hint"] = Label(_("Press OK to toggle the selection"))
		SatList = []
		for sat in nimmanager.getSatList():
			selected = False
			if isinstance(userSatlist, str) and str(sat[0]) in userSatlist:
				selected = True
			SatList.append((sat[0], sat[1], sat[2], selected))
		sat_list = [SelectionEntryComponent(x[1], x[0], x[2], x[3]) for x in SatList]
		self["list"] = SelectionList(sat_list, enableWrapAround=True)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"green": self.save,
			"yellow": self.sortBy,
			"blue": self["list"].toggleAllSelection,
			"save": self.save,
			"cancel": self.cancel,
			"ok": self["list"].toggleSelection,
		}, -2)
		self.setTitle(_("Select satellites"))

	def save(self):
		val = [x[0][1] for x in self["list"].list if x[0][3]]
		self.close(str(val))

	def cancel(self):
		self.close(None)

	def sortBy(self):
		lst = self["list"].list
		if len(lst) > 1:
			menu = [(_("Reverse list"), "2"), (_("Standard list"), "1")]
			connected_sat = [x[0][1] for x in lst if x[0][3]]
			if len(connected_sat) > 0:
				menu.insert(0, (_("Connected satellites"), "3"))

			def sortAction(choice):
				if choice:
					reverse_flag = False
					sort_type = int(choice[1])
					if choice[1] == "2":
						sort_type = reverse_flag = 1
					elif choice[1] == "3":
						reverse_flag = not reverse_flag
					self["list"].sort(sortType=sort_type, flag=reverse_flag)
					self["list"].moveToIndex(0)
			self.session.openWithCallback(sortAction, ChoiceBox, title=_("Select sort method:"), list=menu)
