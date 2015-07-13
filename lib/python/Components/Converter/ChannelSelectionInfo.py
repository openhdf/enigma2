#
# ChannelSelectionInfo Converter by mcbain // v0.1 // 20111109
#
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr
from enigma import eServiceCenter, eEPGCache, eServiceReference
from time import localtime

class ChannelSelectionInfo(Converter, object):
	Reference = 1
	NextEventTitle = 2
	NextEventStartStopTime = 3
	NextEventStartTime = 4
	NextEventStopTime = 5
	NextEventDuration = 6
	NextEventFull = 7

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = {
		 'Reference': self.Reference,
		 'NextEventTitle': self.NextEventTitle,
		 'NextEventStartStopTime': self.NextEventStartStopTime,
		 'NextEventStartTime': self.NextEventStartTime,
		 'NextEventStopTime': self.NextEventStopTime,
		 'NextEventDuration': self.NextEventDuration,
		 'NextEventFull': self.NextEventFull,
		}[type]
		self.epgcache = eEPGCache.getInstance()

	@cached
	def getText(self):
		service = self.source.service
		if service is None:
			return ''

		if self.type == self.Reference:
			marker = (service.flags & eServiceReference.isMarker) == (eServiceReference.isMarker)
			if marker:
				return ''
			refId=''
			sname=service.toString()
			pos=sname.rfind(':')
			if pos != -1:
				refId = ''+sname[:-1]
			return refId

		if (self.type >= self.NextEventTitle and self.type <= self.NextEventFull):
			eventNext=''
			list = self.epgcache.lookupEvent(
			 ['IBDCTSERNX',
			 (service.toString(), 1, -1)]
			)
			if len(list) > 0:
				eventNext = list[0]
				if eventNext[4]:
					if self.type == self.NextEventTitle:
						return str(eventNext[4])

					t_start = localtime(eventNext[1])
					t_stop = localtime(eventNext[1]+eventNext[2])
					eventStartTime = '%02d:%02d' % (t_start.tm_hour, t_start.tm_min)
					eventStopTime = '%02d:%02d' % (t_stop.tm_hour, t_stop.tm_min)
					duration = '%d min' % (eventNext[2] / 60)

					if self.type == self.NextEventStartTime:
						return eventStartTime
					if self.type == self.NextEventStopTime:
						return eventStopTime
					if self.type == self.NextEventStartStopTime:
						return eventStartTime + ' - ' + eventStopTime
					if self.type == self.NextEventDuration:
						return duration
					if self.type == self.NextEventFull:
						return '%s  %s\n%s' % (eventStartTime, duration, eventNext[4])
			else:
				return ' '
		return ''

	text = property(getText)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
			Converter.changed(self, what)