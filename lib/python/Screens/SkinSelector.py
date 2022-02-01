# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_LCDSKIN, SCOPE_SKIN


class SkinSelector(Screen, HelpableScreen):
	skin = ["""
	<screen name="SkinSelector" position="center,center" size="%d,%d">
		<widget name="preview" position="center,%d" size="%d,%d" alphatest="blend" />
		<widget source="skins" render="Listbox" position="center,%d" size="%d,%d" enableWrapAround="1" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{
				"template": [
					MultiContentEntryText(pos = (%d, 0), size = (%d, %d), font = 0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1),
					MultiContentEntryText(pos = (%d, 0), size = (%d, %d), font = 0, flags = RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text = 2)
				],
				"fonts": [gFont("Regular",%d)],
				"itemHeight": %d
				}
			</convert>
		</widget>
		<widget source="description" render="Label" position="center,e-%d" size="%d,%d" font="Regular;%d" valign="center" />
		<widget source="key_red" render="Label" position="%d,e-%d" size="%d,%d" backgroundColor="key_red" font="Regular;%d" foregroundColor="key_text" halign="center" valign="center" />
		<widget source="key_green" render="Label" position="%d,e-%d" size="%d,%d" backgroundColor="key_green" font="Regular;%d" foregroundColor="key_text" halign="center" valign="center" />
	</screen>""",
		670, 570,
		10, 356, 200,
		230, 650, 240,
		10, 350, 30,
		370, 260, 30,
		25,
		30,
		85, 650, 25, 20,
		10, 50, 140, 40, 20,
		160, 50, 140, 40, 20
	]

	def __init__(self, session, screenTitle=_("GUI Skin")):
		Screen.__init__(self, session, mandatoryWidgets=["description", "skins"])
		HelpableScreen.__init__(self)

		element = domScreens.get("SkinSelector", (None, None))[0]
		Screen.setTitle(self, screenTitle)
		self.rootDir = resolveFilename(SCOPE_SKIN)
		self.config = config.skin.primary_skin
		self.current = currentPrimarySkin
		self.xmlList = ["skin.xml"]
		self.onChangedEntry = []
		self["skins"] = List(enableWrapAround=True)
		self["preview"] = Pixmap()
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["introduction"] = StaticText(_("Press OK to activate the selected skin."))
		self["SkinList"] = MenuList(self.skinlist)
		self["Preview"] = Pixmap()
		self.skinlist.sort()

		self["actions"] = NumberActionMap(["SetupActions", "DirectionActions", "TimerEditActions", "ColorActions"],
		{
			"ok": self.ok,
			"cancel": self.close,
			"red": self.close,
			"green": self.ok,
			"up": self.up,
			"down": self.down,
			"left": self.left,
			"right": self.right,
			"log": self.info,
		}, -1)

		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.showPic)

		self.onLayoutFinish.append(self.layoutFinished)

	def showPic(self, picInfo=""):
		ptr = self.picload.getData()
		if ptr is not None:
			self["Preview"].instance.setPixmap(ptr.__deref__())
			self["Preview"].show()

	def layoutFinished(self):
		self.picload.setPara((self["Preview"].instance.size().width(), self["Preview"].instance.size().height(), 0, 0, 1, 1, "#00000000"))
		tmp = self.config.value.find("/" + self.SKINXML)
		if tmp != -1:
			tmp = self.config.value[:tmp]
			idx = 0
			for skin in self.skinlist:
				if skin == tmp:
					break
				idx += 1
			if idx < len(self.skinlist):
				self["SkinList"].moveToIndex(idx)
		self.loadPreview()

	def ok(self):
		if self["SkinList"].getCurrent() == self.DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.SKINXML)
		elif self["SkinList"].getCurrent() == self.PICONDEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICONSKINXML)
		else:
			skinfile = self["SkinList"].getCurrent()
			skinfile = os.path.join(skinfile, self.SKINXML)

		print("Skinselector: Selected Skin: " + self.root + skinfile)
		self.config.value = skinfile
		self.config.save()
		configfile.save()
		restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _("GUI needs a restart to apply a new skin\nDo you want to restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def up(self):
		self["SkinList"].up()
		self.loadPreview()

	def down(self):
		self["SkinList"].down()
		self.loadPreview()

	def left(self):
		self["SkinList"].pageUp()
		self.loadPreview()

	def right(self):
		self["SkinList"].pageDown()
		self.loadPreview()

	def info(self):
		aboutbox = self.session.open(MessageBox, _("Enigma2 skin selector"), MessageBox.TYPE_INFO)
		aboutbox.setTitle(_("About..."))

	def loadPreview(self):
		if self["SkinList"].getCurrent() == self.DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "prev.png")
		elif self["SkinList"].getCurrent() == self.PICONDEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "piconprev.png")
		else:
			pngpath = self["SkinList"].getCurrent()
			try:
				pngpath = os.path.join(os.path.join(self.root, pngpath), "prev.png")
			except:
				pass

		if not os.path.exists(pngpath):
			pngpath = resolveFilename(SCOPE_ACTIVE_SKIN, "noprev.png")

		if self.previewPath != pngpath:
			self.previewPath = pngpath

		self.picload.startDecode(self.previewPath)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)


class SkinSelector(Screen, SkinSelectorBase):
	SKINXML = "skin.xml"
	DEFAULTSKIN = "< Default >"
	PICONSKINXML = None
	PICONDEFAULTSKIN = None

	skinlist = []
	root = os.path.join(eEnv.resolve("${datadir}"), "enigma2")

	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		SkinSelectorBase.__init__(self, args)
		Screen.setTitle(self, _("Skin setup"))
		self.skinName = "SkinSelector"
		self.config = config.skin.primary_skin


class LcdSkinSelector(Screen, SkinSelectorBase):
	SKINXML = "skin_display.xml"
	DEFAULTSKIN = "< Default >"
	PICONSKINXML = "skin_display_picon.xml"
	PICONDEFAULTSKIN = "< Default with Picon >"

	skinlist = []
	root = os.path.join(eEnv.resolve("${datadir}"), "enigma2/display/")

	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		SkinSelectorBase.__init__(self, args)
		Screen.setTitle(self, _("Skin setup"))
		self.skinName = "SkinSelector"
		self.config = config.skin.display_skin
