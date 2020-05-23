installdir = $(pkglibdir)/python/Plugins/SystemPlugins

SUBDIRS = SoftwareManager PositionerSetup Satfinder \
	VideoTune Hotplug CableScan DiseqcTester \
	DefaultServicesScanner CommonInterfaceAssignment \
	HdmiCEC VideoClippingSetup SatelliteEquipmentControl \
	VideoEnhancement WirelessLan NetworkWizard FastScan \
	SABnzbdSetup OSD3DSetup DeviceManager SwapManager LCNScanner

if DREAMBOX
SUBDIRS += FrontprocessorUpgrade NFIFlash
endif

if DM900
SUBDIRS += FSBLUpdater
endif

install_PYTHON = __init__.py
