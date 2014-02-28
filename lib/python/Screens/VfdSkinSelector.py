from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
import Components.config
from Components.Label import Label
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import path, walk
from enigma import eEnv
from skin import *
import os

class VFDSkinSelector(Screen):
	skin = """
		<screen name="VFD Skin-Selector" position="center,center" size="700,400" title="VFD Skin-Selector" transparent="0">
			<eLabel text="Select skin:" position="50,30" size="250,26" zPosition="1" foregroundColor="#FFE500" font="Regular;22" halign="left" />
			<eLabel text="Preview:" position="380,30" size="250,26" zPosition="1" foregroundColor="#FFE500" font="Regular;22" halign="left" />
			<widget name="SkinList" render="Listbox" position="50,60" size="270,200" zPosition="1" enableWrapAround="1" scrollbarMode="showOnDemand" />
			<widget name="Preview" position="380,65" size="280,210" zPosition="1" backgroundColor="background" transparent="0" alphatest="on" />
			<eLabel text="Select your skin and press OK to activate the selected skin" position="0,307" halign="center" size="700,26" zPosition="1" foregroundColor="#FFE500" font="Regular;22" />
			<ePixmap name="red" position="50,350" zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="220,350" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="520,350" zPosition="1" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="50,350" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
			<widget name="key_green" position="220,350" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
			<widget name="key_blue" position="520,350" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		</screen>"""

	skinlist = []
	root = eEnv.resolve("/usr/share/enigma2/display/")

	def __init__(self, session, args = None):

		Screen.__init__(self, session)

		self.list = []
		self.previewPath = ""
		self.actual = None
		path.walk(self.root, self.find, "")

		self["key_red"] = StaticText(_("Close"))
		self["introduction"] = StaticText(_("Press OK to activate the selected skin."))
		self.skinlist.sort()
		self["SkinList"] = MenuList(self.list)
		self["Preview"] = Pixmap()

		self["actions"] = NumberActionMap(["WizardActions", "OkCancelActions", "ColorActions"],
		{
			"ok": self.ok,
			"back": self.close,
			"red": self.close,
			"green": self.ok,
			"up": self.up,
			"down": self.down,
			"left": self.left,
			"right": self.right,
			"blue": self.info,
		}, -1)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["key_blue"] = Label(_("Info"))
		self.fill()
		self.onLayoutFinish.append(self.layoutFinished)


	def fill(self):
		i = 0
		self.filesArray = sorted(filter(lambda x: x.endswith('.xml'), os.listdir(self.root)))
		config.skin.display_skin = ConfigSelection(choices = self.filesArray)
		while i < len(self.filesArray):
			self.list.append((_(self.filesArray[i].split('.')[0]), "chose"))
			i = i + 1
		else:
			pass
		idx = 0

	def layoutFinished(self):
		tmp = "config.skin.display_skin.getValue()"
		tmp = eval(tmp)
		idx = 0
		i = 0
		while i < len(self.list):
			if tmp.split('.')[0] in self.list[i][0]:
				idx = i
				break
			else:
				pass
			i += 1
		self["SkinList"].moveToIndex(idx)
		self.loadPreview()

	def up(self):
		self["SkinList"].up()
		self["SkinList"].l.getCurrentSelection()
		self.loadPreview()

	def down(self):
		self["SkinList"].down()
		self["SkinList"].l.getCurrentSelection()
		self.loadPreview()

	def left(self):
		self["SkinList"].pageUp()
		self["SkinList"].l.getCurrentSelection()
		self.loadPreview()

	def right(self):
		self["SkinList"].pageDown()
		self["SkinList"].l.getCurrentSelection()
		self.loadPreview()

	def info(self):
		aboutbox = self.session.open(MessageBox,_("\nVFD Skin-Selector\nby satinfo & henrylicious (thank you for support)\n\nPlugin to select skin for VFD-Display\n\n - for GigaBlue UE and GigaBlue Quad\n - for VU+ Ultimo and VU+ Duo2"), MessageBox.TYPE_INFO)
		aboutbox.setTitle(_("About..."))

	def find(self, arg, dirname, names):
		for x in names:
			if x.startswith("skinvfd") and x.endswith(".xml"):
				if dirname <> self.root:
					subdir = dirname[19:]
					skinname = x
					skinname = subdir + "/" + skinname
					self.list.append(skinname)
				else:
					skinname = x
					self.list.append(skinname)

	def ok(self):
		skinfile = self["SkinList"].getCurrent()[0] + ".xml"
		addSkin(skinfile, SCOPE_CONFIG)
		config.skin.display_skin.value = skinfile
		config.skin.display_skin.save()
		print "Selected Value", config.skin.display_skin.getValue()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply new skin.\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def loadPreview(self):
		pngpath = self["SkinList"].l.getCurrentSelection()[0] + "_prev.png"
		try:
			pngpath = self.root + pngpath
		except AttributeError:
			pass
		if not os.path.exists(pngpath):
			pngpath = "/usr/share/enigma2/display/noprev.png"
		if self.previewPath != pngpath:
			self.previewPath = pngpath
		self["Preview"].instance.setPixmapFromFile(self.previewPath)
		Screen.hide(self)
		Screen.show(self)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
