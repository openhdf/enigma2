# -*- coding: utf-8 -*-
#
# ServiceReference to PiconName  - Converter
#
# Coded by dre (c) 2014 - 2016
# Support: www.dreambox-tools.info
# E-Mail: dre@dreambox-tools.info
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Property GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Property GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Property GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
#

from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eServiceCenter, eServiceReference, iPlayableServicePtr, iServiceInformation

class RefToPiconName(Converter, object):
	REFERENCE = 0
	NAME = 1
	
	def __init__(self, type):
		if type == "Name":
			self.type = self.NAME
		else:
			self.type = self.REFERENCE
				
		Converter.__init__(self, type)

	@cached
	def getText(self):
		ref = self.source.service
		
		if ref is not None:
			if not isinstance(ref, iPlayableServicePtr):
				#bouquet or marker
				if ref.flags & (eServiceReference.isDirectory|eServiceReference.isMarker):
					info = eServiceCenter.getInstance().info(ref)
					if info:
						return info.getName(ref).replace(" ","_")
				#alternatives
				elif ref.flags & (eServiceReference.isGroup):
					if self.type == self.NAME:
						return eServiceCenter.getInstance().list(ref).getContent("N")[0].replace(" ","_")				
					return eServiceCenter.getInstance().list(ref).getContent("S")[0]
				#channel
				if self.type == self.NAME:
					info = eServiceCenter.getInstance().info(ref)
					if info:
						return info.getName(ref).replace(" ", "_")				
				return ref.toString()
			else:
				info = ref and ref.info()
				service = None
			
				if info:
					sRef = service and info.getInfoString(service, iServiceInformation.sServiceRef) or info.getInfoString(iServiceInformation.sServiceref)
					if sRef is None or sRef is "" or self.type == self.NAME:
						return info.getName().replace(" ","_")
					else:
						return sRef
		return ""
		
	text = property(getText)
