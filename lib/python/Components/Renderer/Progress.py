from __future__ import absolute_import
from Components.VariableValue import VariableValue
from Components.Renderer.Renderer import Renderer

from enigma import eSlider


class Progress(VariableValue, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableValue.__init__(self)
		self.__start = 0
		self.__end = 100

	GUI_WIDGET = eSlider

	def changed(self, what):
		if what[0] == self.CHANGED_CLEAR:
			(self.range, self.value) = ((0, 1), 0)
			return

		_range = self.source.range or 100
		value = self.source.value
		if value is None:
			value = 0
		if _range > 2**31 - 1:
			_range = 2**31 - 1
		if value > _range:
			value = _range
		if value < 0:
			value = 0
		(self.range, self.value) = ((0, _range), value)

	def postWidgetCreate(self, instance):
		instance.setRange(self.__start, self.__end)

	def setRange(self, _range):
		(self.__start, self.__end) = _range
		if self.instance is not None:
			self.instance.setRange(self.__start, self.__end)

	def getRange(self):
		return self.__start, self.__end

	_range = property(getRange, setRange)
