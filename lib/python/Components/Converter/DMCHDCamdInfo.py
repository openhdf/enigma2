#
#  CamdInfo - Converter
#
#  Coded by weazle (c) 2010
#  Support: www.dreambox-tools.info
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#


# <widget source="session.CurrentService" render="Label" position="189,397" zPosition="4" size="350,20" noWrap="1" valign="center" halign="center" font="Regular;14" foregroundColor="clText" transparent="1"  backgroundColor="#20002450">
#	<convert type="CamdInfo">Camd</convert>
# </widget>			

from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists

class DMCHDCamdInfo(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
		   return ""
		camd = None
                	
		# OoZooN
		if fileExists("/tmp/cam.info"):
			try:
				camdlist = open("/tmp/cam.info", "r")
			except:
				return None
			
		# Merlin2	
		elif fileExists("/etc/clist.list"):
			try:
		   		camdlist = open("/etc/clist.list", "r")
		   	except:
				return None
		
		# GP3
		elif fileExists("/usr/lib/enigma2/python/Plugins/Bp/geminimain/lib/libgeminimain.so"):
			try:
				from Plugins.Bp.geminimain.plugin import GETCAMDLIST
				from Plugins.Bp.geminimain.lib import libgeminimain
				
				camdl = libgeminimain.getPyList(GETCAMDLIST)
				camd = None
				for x in camdl:
					if x[1] == 1:
						camd = x[2] 
				return camd
		   	except:
				return None
		
		else:
			camdlist = None
		
		if camdlist is not None:
			for current in camdlist:
				camd = current
			camdlist.close()
			return camd
		elif camd is not None:
			return camd  
		else:
			return ""

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)




