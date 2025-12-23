from Components.Sources.Source import Source
from Components.Element import cached


class List(Source):
	"""The datasource of a listbox. Currently, the format depends on the used converter. So
if you put a simple string list in here, you need to use a StringList converter, if you are
using a "multi content list styled"-list, you need to use the StaticMultiList converter, and
setup the "fonts".

This has been done so another converter could convert the list to a different format, for example
to generate HTML."""

	def __init__(self, list=[], enableWrapAround=True, item_height=25, fonts=[]):
		Source.__init__(self)
		self.__list = list
		self.onSelectionChanged = []
		self.item_height = item_height
		self.fonts = fonts
		self.disable_callbacks = False
		self.enableWrapAround = enableWrapAround
		self.__style = "default" # style might be an optional string which can be used to define different visualisations in the skin
		self.__current = None  # current element set from connected GUI element
		self.__index = 0  # current index set from connected GUI element
		self.connectedGuiElement = None  # manuallyconnected GUI element

	def setList(self, list):
		self.__list = list
		self.changed((self.CHANGED_ALL,))

	list = property(lambda self: self.__list, setList)

	def entry_changed(self, index):
		if not self.disable_callbacks:
			self.downstream_elements.entry_changed(index)

	def listUpdated(self):
		for method in self.onListUpdated:
			method()

	def modifyEntry(self, index, data):
		self.__list[index] = data
		self.entry_changed(index)

	def count(self):
		return len(self.__list)

	def selectionChanged(self, index):
		if self.disable_callbacks:
			return

		# update all non-master targets
		for x in self.downstream_elements:
			if x is not self.master:
				x.index = index

		for x in self.onSelectionChanged:
			x()

	# this is for manually set which is the GUI element connected with the list
	# For use in case of addons where there is no source so to rely on the master
	def setConnectedGuiElement(self, guiElement):
		self.connectedGuiElement = guiElement
		index = guiElement.instance.getCurrentIndex()
		self.__current = self.listData[index]
		self.__index = index
		self.changed((self.CHANGED_ALL,))

	@cached
	def getCurrent(self):
		return self.master is not None and self.master.current

	current = property(getCurrent)

	def setIndex(self, index):
		if self.master is not None:
			self.master.index = index
			self.selectionChanged(index)

	@cached
	def getIndex(self):
		if self.master is not None:
			return self.master.index
		else:
			return 0

	setCurrentIndex = setIndex

	index = property(getIndex, setIndex)

	def selectNext(self):
		if self.getIndex() + 1 >= self.count():
			if self.enableWrapAround:
				self.index = 0
		else:
			self.index += 1
		self.setIndex(self.index)

	def selectPrevious(self):
		if self.getIndex() - 1 < 0:
			if self.enableWrapAround:
				self.index = self.count() - 1
		else:
			self.index -= 1
		self.setIndex(self.index)

	@cached
	def getStyle(self):
		return self.__style

	def setStyle(self, style):
		if self.__style != style:
			self.__style = style
			self.changed((self.CHANGED_SPECIFIC, "style"))

	style = property(getStyle, setStyle)

	@cached
	def getCurrentIndex(self):
		return self.master.index if self.master is not None and hasattr(self.master, "index") else self.__index

	def setCurrentIndex(self, index):
		if self.master is not None:
			if hasattr(self.master, "index"):
				self.master.index = index
			else:
				self.__index = index
			self.selectionChanged(index)
		if self.connectedGuiElement is not None:
			self.connectedGuiElement.moveSelection(index)

	index = property(getCurrentIndex, setCurrentIndex)

	def updateList(self, list):
		"""Changes the list without changing the selection or emitting changed Events"""
		assert len(list) == len(self.__list)
		old_index = self.index
		self.disable_callbacks = True
		self.list = list
		self.index = old_index
		self.disable_callbacks = False

	def pageUp(self):
		try:
			instance = self.master.master.instance
			instance.moveSelection(instance.pageUp)
		except AttributeError:
			return

	def pageDown(self):
		try:
			instance = self.master.master.instance
			instance.moveSelection(instance.pageDown)
		except AttributeError:
			return

	def up(self):
		self.selectPrevious()

	def down(self):
		self.selectNext()

	def getSelectedIndex(self):
		return self.getIndex()

	def getSelectedIndex(self):
		return self.getCurrentIndex()

	def getIndex(self):
		return self.getCurrentIndex()
