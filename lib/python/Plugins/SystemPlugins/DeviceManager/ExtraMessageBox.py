# for localized messages
from enigma import eTimer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label


def MessageBoxEntry(name, picture):
	pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/DeviceManager/icons/" + picture))
	if not pixmap:
		pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/DeviceManager/icons/empty.png"))

	return (pixmap, name)


class ExtraMessageBox(Screen):
	skin = """
	<screen name="ExtraMessageBox" position="center,center" size="460,430" title=" ">
		<widget name="message" position="10,10" size="440,25" font="Regular;20" />
		<widget source="menu" render="Listbox" position="20,90" size="420,360" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
					MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),
					MultiContentEntryText(pos = (65, 10), size = (425, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
					],
					"fonts": [gFont("Regular", 22)],
					"itemHeight": 48
				}
			</convert>
		</widget>
	</screen>"""

	def __init__(self, session, message="", title="", menulist=[], type=0, exitid=-1, default=0, timeout=0):
		# type exist for compability... will be ignored
		Screen.__init__(self, session)
		self.session = session
		self.ctitle = title
		self.exitid = exitid
		self.default = default
		self.timeout = timeout
		self.elapsed = 0

		self.list = []
		for item in menulist:
			self.list.append(MessageBoxEntry(item[0], item[1]))

		self['menu'] = List(self.list)
		self["menu"].onSelectionChanged.append(self.selectionChanged)

		self["message"] = Label(message)
		self["actions"] = ActionMap(["SetupActions"],
		{
			"ok": self.ok,
			"cancel": self.cancel
		}, -2)

		self.onLayoutFinish.append(self.layoutFinished)

		self.timer = eTimer()
		self.timer.callback.append(self.timeoutStep)
		if self.timeout > 0:
			self.timer.start(1000, 1)

	def selectionChanged(self):
		self.timer.stop()
		self.setTitle(self.ctitle)

	def timeoutStep(self):
		self.elapsed += 1
		if self.elapsed == self.timeout:
			self.ok()
		else:
			self.setTitle("%s - %d" % (self.ctitle, self.timeout - self.elapsed))
			self.timer.start(1000, 1)

	def layoutFinished(self):
		if self.timeout > 0:
			self.setTitle("%s - %d" % (self.ctitle, self.timeout))
		else:
			self.setTitle(self.ctitle)
		self['menu'].setCurrentIndex(self.default)

	def ok(self):
		index = self['menu'].getIndex()
		self.close(index)

	def cancel(self):
		if self.exitid > -1:
			self.close(self.exitid)
