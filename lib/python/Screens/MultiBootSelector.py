
from os import mkdir
from os import path as os_path
from shutil import copyfile

from enigma import eRCInput, fbClass

from Components.ActionMap import ActionMap
from Components.ChoiceList import ChoiceEntryComponent, ChoiceList
from Components.Console import Console
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import BoxInfo
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.BoundFunction import boundFunction
from Tools.Directories import copyfile, pathExists
from Tools.Multiboot import GetCurrentImage, GetCurrentImageMode, GetImagelist


class MultiBootSelector(Screen):

	skin = """
	<screen name="Multiboot Image Selector" position="center,center" size="750,900" flags="wfNoBorder" backgroundColor="transparent">
		<eLabel name="b" position="0,0" size="750,700" backgroundColor="#00ffffff" zPosition="-2" />
		<eLabel name="a" position="1,1" size="748,698" backgroundColor="#00000000" zPosition="-1" />
		<widget source="Title" render="Label" position="60,10" foregroundColor="#00ffffff" size="480,50" halign="left" font="Regular; 28" backgroundColor="#00000000" />
		<eLabel name="line" position="1,60" size="748,1" backgroundColor="#00ffffff" zPosition="1" />
		<eLabel name="line2" position="1,250" size="748,4" backgroundColor="#00ffffff" zPosition="1" />
		<widget name="config" position="2,280" size="730,380" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00e5b243" />
		<widget source="description" render="Label" position="2,80" size="730,30" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="options" render="Label" position="2,130" size="730,60" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_red" render="Label" position="30,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_green" render="Label" position="200,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<eLabel position="20,200" size="6,40" backgroundColor="#00e61700" /> <!-- Should be a pixmap -->
		<eLabel position="190,200" size="6,40" backgroundColor="#0061e500" /> <!-- Should be a pixmap -->
	</screen>
	"""

	def __init__(self, session, *args):
		Screen.__init__(self, session)
		screentitle = _("Multiboot Image Selector")
		self["key_red"] = StaticText(_("Cancel"))
		if not BoxInfo.getItem("HasSDmmc") or BoxInfo.getItem("HasSDmmc") and pathExists('/dev/%s4' % (BoxInfo.getItem("canMultiBoot")[2])):
			self["description"] = StaticText(_("Use the cursor keys to select an installed image and then Reboot button."))
		else:
			self["description"] = StaticText(_("SDcard is not initialised for multiboot - Exit and use MultiBoot Image Manager to initialise"))
		self["options"] = StaticText(_(" "))
		self["key_green"] = StaticText(_("Reboot"))
		if BoxInfo.getItem("canMode12"):
			self["options"] = StaticText(_("Mode 1 suppports Kodi, PiP may not work.\nMode 12 supports PiP, Kodi may not work."))
		self["config"] = ChoiceList(list=[ChoiceEntryComponent('', ((_("Retrieving image startups - Please wait...")), "Queued"))])
		imagedict = []
		self.getImageList = None
		self.mountDir = "/tmp/startupmount"
		self.callLater(self.getBootOptions)
		self.title = screentitle

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "KeyboardInputActions", "MenuActions"],
		{
			"red": boundFunction(self.close, None),
			"green": self.reboot,
			"ok": self.reboot,
			"cancel": boundFunction(self.close, None),
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
			"upRepeated": self.keyUp,
			"downRepeated": self.keyDown,
			"leftRepeated": self.keyLeft,
			"rightRepeated": self.keyRight,
			"menu": boundFunction(self.close, True),
		}, -1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.title)

	def cancel(self, value=None):
		self.container = Console()
		self.container.ePopen("umount %s" % self.mountDir, boundFunction(self.unmountCallback, value))

	def unmountCallback(self, value, data=None, retval=None, extra_args=None):
		self.container.killAll()
		if not os_path.ismount(self.mountDir):
			rmdir(self.mountDir)
		self.close(value)

	def getBootOptions(self, value=None):
		self.container = Console()
		if os_path.isdir(self.mountDir) and os_path.ismount(self.mountDir):
			self.getImagesList()
		else:
			if not os_path.isdir(self.mountDir):
				mkdir(self.mountDir)
			self.container.ePopen("mount %s %s" % (BoxInfo.getItem("MBbootdevice"), self.mountDir), self.getImagesList)

	def getImagesList(self, data=None, retval=None, extra_args=None):
		self.container.killAll()
		self.getImageList = GetImagelist(self.getImagelistCallback)

	def getImagelistCallback(self, imagedict):
		_list = []
		mode = GetCurrentImageMode() or 0
		currentimageslot = GetCurrentImage()
		print("[MultiBootSelector] reboot1 slot:", currentimageslot)
		current = "  %s" % _("(current image)")
		slotSingle = _("Slot %s: %s%s")
		slotMulti = _("Slot %s: %s - Mode %d%s")
		if imagedict:
			indextot = 0
			for index, x in enumerate(sorted(list(imagedict.keys()))):
				if imagedict[x]["imagename"] != _("Empty slot"):
					if BoxInfo.getItem("canMode12"):
						_list.insert(index, ChoiceEntryComponent("", (slotMulti % (x, imagedict[x]["imagename"], 1, current if x == currentimageslot and mode != 12 else ""), (x, 1))))
						_list.append(ChoiceEntryComponent("", (slotMulti % (x, imagedict[x]["imagename"], 12, current if x == currentimageslot and mode == 12 else ""), (x, 12))))
						indextot = index + 1
					else:
						_list.append(ChoiceEntryComponent("", (slotSingle % (x, imagedict[x]["imagename"], current if x == currentimageslot else ""), (x, 1))))
			if BoxInfo.getItem("canMode12"):
				_list.insert(indextot, " ")
		else:
			_list.append(ChoiceEntryComponent("", ((_("No images found")), "Waiter")))
		self["config"].setList(_list)

	def reboot(self):
		self.currentSelected = self["config"].l.getCurrentSelection()
		if self.currentSelected[0][1] != "Queued":
			slot = self.currentSelected[0][1][0]
			boxmode = self.currentSelected[0][1][1]
			message = _("Do you want to reboot now the image in startup %s?") % slot
			print("[MultiBootSelector] reboot2 reboot slot = %s, " % slot)
			print("[MultiBootSelector] reboot2 reboot boxmode = %s, " % boxmode)
			print("[MultiBootSelector] reboot3 slotinfo = %s" % BoxInfo.getItem("canMultiBoot"))
			if BoxInfo.getItem("canMode12"):
				if "BOXMODE" in BoxInfo.getItem("canMultiBoot")[slot]['startupfile']:
					startupfile = os_path.join(self.mountDir, "%s_%s" % (BoxInfo.getItem("canMultiBoot")[slot]['startupfile'].rsplit('_', 1)[0], boxmode))
					copyfile(startupfile, os_path.join(self.mountDir, "STARTUP"))
				else:
					f = open(os_path.join(self.mountDir, BoxInfo.getItem("canMultiBoot")[slot]['startupfile']), "r").read()
					if boxmode == 12:
						f = f.replace("boxmode=1'", "boxmode=12'").replace("%s" % BoxInfo.getItem("canMode12")[0], "%s" % BoxInfo.getItem("canMode12")[1])
					open(os_path.join(self.mountDir, "STARTUP"), "w").write(f)
			else:
				copyfile(os_path.join(self.mountDir, BoxInfo.getItem("canMultiBoot")[slot]["startupfile"]), os_path.join(self.mountDir, "STARTUP"))
			self.session.openWithCallback(self.restartImage, MessageBox, message, MessageBox.TYPE_YESNO, timeout=20)

	def restartImage(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close()

	def selectionChanged(self):
		currentSelected = self["config"].l.getCurrentSelection()

	def keyLeft(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.selectionChanged()

	def keyRight(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.selectionChanged()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.selectionChanged()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.selectionChanged()


class QuickBootSelector(Screen):

	def __init__(self, session, *args):
		Screen.__init__(self, session)
		screentitle = _("QuickBoot Image Selector")
		self.skinName = "MultiBootSelector"
		self["key_red"] = StaticText(_("Cancel"))
		if not BoxInfo.getItem("HasSDmmc") or BoxInfo.getItem("HasSDmmc") and pathExists('/dev/%s4' % (BoxInfo.getItem("canMultiBoot")[2])):
			self["description"] = StaticText(_("Use the cursor keys to select an installed image and then Start button."))
		else:
			self["description"] = StaticText(_("SDcard is not initialised for multiboot - Exit and use MultiBoot Image Manager to initialise"))
		self["options"] = StaticText(_(" "))
		self["key_green"] = StaticText(_("Start"))
		self["config"] = ChoiceList(list=[ChoiceEntryComponent('', ((_("Retrieving image startups - Please wait...")), "Queued"))])
		imagedict = []
		self.getImageList = None
		self.mountDir = "/tmp/startupmount"
		self.callLater(self.getBootOptions)
		self.title = screentitle

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "KeyboardInputActions", "MenuActions"],
		{
			"red": boundFunction(self.close, None),
			"green": self.reboot,
			"ok": self.reboot,
			"cancel": boundFunction(self.close, None),
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
			"upRepeated": self.keyUp,
			"downRepeated": self.keyDown,
			"leftRepeated": self.keyLeft,
			"rightRepeated": self.keyRight,
			"menu": boundFunction(self.close, True),
		}, -1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.title)

	def getBootOptions(self, value=None):
		self.container = Console()
		if os_path.isdir(self.mountDir) and os_path.ismount(self.mountDir):
			self.getImagesList()
		else:
			if not os_path.isdir(self.mountDir):
				mkdir(self.mountDir)
			self.container.ePopen("mount %s %s" % (BoxInfo.getItem("MBbootdevice"), self.mountDir), self.getImagesList)

	def getImagesList(self, data=None, retval=None, extra_args=None):
		self.container.killAll()
		self.getImageList = GetImagelist(self.getImagelistCallback)

	def getImagelistCallback(self, imagedict):
		_list = []
		currentimageslot = GetCurrentImage()
		current = "  %s" % _("(current image)")
		slotSingle = _("Slot %s: %s%s")
		if imagedict:
			indextot = 0
			for index, x in enumerate(sorted(list(imagedict.keys()))):
				if imagedict[x]["imagename"] != _("Empty slot"):
					_list.append(ChoiceEntryComponent("", (slotSingle % (x, imagedict[x]["imagename"], current if x == currentimageslot else ""), (x, 1))))
		else:
			_list.append(ChoiceEntryComponent("", ((_("No images found")), "Waiter")))
		self["config"].setList(_list)

	def reboot(self):
		self.currentSelected = self["config"].l.getCurrentSelection()
		if self.currentSelected[0][1] != "Queued":
			slot = self.currentSelected[0][1][0]
			boxmode = self.currentSelected[0][1][1]
			message = _("Do you want to reboot now the image in startup %s?") % slot
			self.session.openWithCallback(self.startImage, MessageBox, message, MessageBox.TYPE_YESNO, timeout=20)

	def startImage(self, answer):
		slot = self["config"].l.getCurrentSelection()[0][1][0]
		mtdroot = BoxInfo.getItem("canMultiBoot")[slot]["device"]
		COMMAND = """
#!/bin/bash
mkdir /tmp/quick
mount %s /tmp/quick
mkdir -p /tmp/quick/var/volatile/tmp
mount -o bind /sys /tmp/quick/sys
mount -o bind /proc /tmp/quick/proc
mount -o bind /dev /tmp/quick/dev
mount -o bins /var/volatile/tmp /tmp/quick/var/volatile/tmp
chroot /tmp/quick /bin/bash <<"EOT"
enigma2
EOT
umount /tmp/quick/var/volatile/tmp /tmp/quick/dev /tmp/quick/proc /tmp/quick/sys /tmp/quick
rm /tmp/quickboot.sh
		""" % mtdroot

		if answer is True:
			f = open("/tmp/quickboot.sh", "w")
			f.write(COMMAND)
			f.close()
			self.previousService = self.session.nav.getCurrentlyPlayingServiceReference()
			self.session.nav.stopService()
			fbClass.getInstance().lock()
			eRCInput.getInstance().lock()
			self._startConsole = Console()
			self._startConsole.ePopen("bash /tmp/quickboot.sh", self.e2Stopped)
		else:
			self.close()

	def e2Stopped(self, data, retval, extraArgs):
		eRCInput.getInstance().unlock()
		fbClass.getInstance().unlock()
		if self.previousService:
			self.session.nav.playService(self.previousService)
		self.hide()
		self.show()

	def selectionChanged(self):
		currentSelected = self["config"].l.getCurrentSelection()

	def keyLeft(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.selectionChanged()

	def keyRight(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.selectionChanged()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.selectionChanged()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.selectionChanged()
