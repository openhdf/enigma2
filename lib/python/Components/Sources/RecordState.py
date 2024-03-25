
from enigma import iRecordableService

from Components.config import config
from Components.Element import cached
from Components.RecordingConfig import recType
from Components.Sources.Source import Source
from Components.SystemInfo import BoxInfo


class RecordState(Source):
	def __init__(self, session):
		Source.__init__(self)
		self.records_running = 0
		self.session = session
		session.nav.record_event.append(self.gotRecordEvent)
		self.gotRecordEvent(None, None) # get initial state

	def gotRecordEvent(self, service, event):
		prev_records = self.records_running
		if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
			recs = self.session.nav.getRecordings(False, recType(config.recording.show_rec_symbol_for_rec_types.getValue()))
			if BoxInfo.getItem("LCDsymbol_circle"):
				open(BoxInfo.getItem("LCDsymbol_circle"), "w").write(recs and "1" or "0")
			self.records_running = len(recs)
			if self.records_running != prev_records:
				self.changed((self.CHANGED_ALL,))

	def destroy(self):
		self.session.nav.record_event.remove(self.gotRecordEvent)
		Source.destroy(self)

	@cached
	def getBoolean(self):
		return self.records_running and True or False
	boolean = property(getBoolean)

	@cached
	def getValue(self):
		return self.records_running
	value = property(getValue)
