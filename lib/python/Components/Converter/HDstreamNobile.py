from enigma import iServiceInformation, iPlayableService
from Components.Converter.Converter import Converter
from Components.Element import cached

class HDstreamNobile(Converter, object):
	IS_HD = 0
	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = {"showHDicon": self.IS_HD,}[type]
		self.hook_elements = {self.IS_HD: [iPlayableService.evVideoSizeChanged],}[self.type]

	@cached
	def getBoolean(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return False
		if self.type == self.IS_HD:
			xresol = info.getInfo(iServiceInformation.sVideoWidth)
			yresol = info.getInfo(iServiceInformation.sVideoHeight)
			if (xresol > 800) or (yresol > 700):
				return True
			else:
				return False

	boolean = property(getBoolean)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in self.hook_elements:
			Converter.changed(self, what)




