#######################################################################
#
#    Converter for Enigma2
#    Coded by shamann (c)2012
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#######################################################################
from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceReference, eEPGCache
from Components.Element import cached
from time import localtime
import re

class g16ServiceNameEventNobile(Converter, object):
	NAMEVENT = 0
	NEXTEVENT = 1
	STARTTIME = 2
	DURATION = 3
	ENDTIME = 4
	EXTENDED_DESCRIPTION = 5
	EXTENDED_DESCRIPTION_EVENT = 6
          	
	def __init__(self, type):
		Converter.__init__(self, type)
		self.epgQuery = eEPGCache.getInstance().lookupEventTime
		if type == "NameAndEvent":
			self.type = self.NAMEVENT
		elif type == "NextEvent":
			self.type = self.NEXTEVENT
		elif type == "StartTime":
			self.type = self.STARTTIME
		elif type == "Duration":
			self.type = self.DURATION			
		elif type == "EndTime":
			self.type = self.ENDTIME
		elif type == "ExtendedDescription":
			self.type = self.EXTENDED_DESCRIPTION
		elif type == "ExtendedDescriptionEvent" or type == "ExtendedDescriptionEventSingle":
			self.type = self.EXTENDED_DESCRIPTION_EVENT
      			
	@cached
	def getText(self):
		no_desc = ""
		if self.type != self.EXTENDED_DESCRIPTION_EVENT:
			service = self.source.service
			if isinstance(service, iPlayableServicePtr):
				info = service and service.info()
				ref = None
			else: 
				info = service and self.source.info
				ref = service
			if info is None:
				return no_desc
			if self.type == self.NAMEVENT:
				name = ref and info.getName(ref)
				if name is None:
					name = info.getName()
				name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
				act_event = info and info.getEvent(0)
				if not act_event and info:
					refstr = info.getInfoString(iServiceInformation.sServiceref)
					act_event = self.epgQuery(eServiceReference(refstr), -1, 0)
				if act_event is None:
					return "%s - %s" % (name, no_desc)
				else:
					return "%s - %s" % (name, act_event.getEventName())
			act_event = None				
			try:
				act_event = self.epgQuery(eServiceReference(service.toString()), -1, 1)
			except: pass
			if act_event is None:
				return no_desc
		else:
			act_event = self.source.event
			if act_event is None:
				return no_desc
		if self.type == self.NEXTEVENT:
			return act_event.getEventName()
		elif self.type == self.STARTTIME:
			t = localtime(act_event.getBeginTime())
			return "%02d:%02d" % (t.tm_hour, t.tm_min)
		elif self.type == self.ENDTIME:
			t = localtime(act_event.getBeginTime() + act_event.getDuration())
			return "%02d:%02d" % (t.tm_hour, t.tm_min)
		elif self.type == self.DURATION:
			return "%d min" % (int(act_event.getDuration() / 60))
		elif self.type == self.EXTENDED_DESCRIPTION or self.type == self.EXTENDED_DESCRIPTION_EVENT:
			short = act_event.getShortDescription()
			tmp = act_event.getExtendedDescription()
			if tmp == "" or tmp is None:
				tmp = short		
				if tmp == "" or tmp is None:
					tmp = no_desc
				else:
					tmp = tmp.strip()
			else:
				tmp = tmp.strip()
				if short != "" or short is not None:
					if len(short) > 3:
						if not short[:-2] in tmp:
							tmp = short.strip() + "..." + tmp
			tmp = tmp.replace("\r", " ").replace("\n", " ").replace("\xc2\x8a", " ")
			return re.sub('[\s\t]+', ' ',tmp)
		else:
			return "Error reading EPG data"

	text = property(getText)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart, iPlayableService.evUpdatedEventInfo,):
			Converter.changed(self, what)
