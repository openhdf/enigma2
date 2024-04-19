from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import getReasons
from Components.Sources.StaticText import StaticText
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent
from Components.config import config, configfile
from Components.ActionMap import ActionMap
from Components.Console import Console
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.SystemInfo import BoxInfo
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, getBackupFilename, getBackupPath
from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists, pathExists, fileHas
from Tools.Downloader import downloadWithProgress
from Tools.HardwareInfo import HardwareInfo
from Tools.Multiboot import GetImagelist, GetCurrentImage, GetCurrentImageMode, deleteImage, restoreImages
import os
from urllib.request import urlopen, Request, HTTPError
import xml.etree.ElementTree
import json
import time
import zipfile
import shutil
import tempfile
import struct

from enigma import eEPGCache
from boxbranding import getImageDistro, getBoxType, getMachineBrand, getMachineName

isDevice = False
doBackup = False
multibootslot = ""


def checkimagefiles(files):
	return len([x for x in files if 'kernel' in x and '.bin' in x or x in ('uImage', 'rootfs.bin', 'root_cfe_auto.bin', 'root_cfe_auto.jffs2', 'oe_rootfs.bin', 'e2jffs2.img', 'rootfs.tar.bz2', 'rootfs.ubi')]) == 2


class SelectImage(Screen):
	skin = """<screen name="SelectImage" position="center,center" size="560,440" title="SoftwareManager setup">
		<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget name="list" position="5,50" size="550,350" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="div-h.png" position="0,400" zPosition="1" size="560,2" />
		<widget source="descripion" render="Label" position="5,410" size="550,30" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />
	</screen>"""

	def __init__(self, session, *args):
		Screen.__init__(self, session)
		self.imageBrandDict = {}
		self.jsonlist = {}
		self.imagesList = {}
		self.setIndex = 0
		self.expanded = []
		self.model = getBoxType()
		self.selectedImage = ["OpenHDF", {"url": "https://flash.hdfreaks.cc/openhdf/json/%s" % self.model, "model": self.model}]
		self.models = [self.model]
		self.setTitle(_("Select image"))
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText()
		self["key_yellow"] = StaticText(_("Initialize Multiboot")) if BoxInfo.getItem("canKexec") else StaticText()
		self["key_blue"] = StaticText()
		self["description"] = Label()
		self["list"] = ChoiceList(list=[ChoiceEntryComponent('', ((_("Retrieving image list - Please wait...")), "Waiter"))])

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "KeyboardInputActions", "MenuActions"],
		{
			"ok": self.keyOk,
			"cancel": boundFunction(self.close, None),
			"red": boundFunction(self.close, None),
			"green": self.keyOk,
			"yellow": self.keyYellow,
			"blue": self.otherImages,
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

		self.callLater(self.getImagesList)

	def getImagesList(self):

		def getImages(path, files):
			for imageFile in files:
				try:
					if checkimagefiles([x.split(os.sep)[-1] for x in zipfile.ZipFile(imageFile).namelist()]):
						imagetyp = _("Downloaded Images")
						if 'backup' in imageFile.split(os.sep)[-1]:
							imagetyp = _("Fullbackup Images")
						if imagetyp not in self.imagesList:
							self.imagesList[imagetyp] = {}
						self.imagesList[imagetyp][imageFile] = {'link': imageFile, 'name': imageFile.split(os.sep)[-1]}
				except Exception:
					print("[FlashImage] getImagesList Error: Unable to extract file list from Zip file '%s'!" % imageFile)

		def checkModels(imageFile):
			for model in self.models:
				if '-%s-' % model in imageFile:
					return True
			return False

		def conditional_sort(ls, f):
			y = iter(reversed(sorted(w for w in ls if f(w))))
			return [w if not f(w) else next(y) for w in ls]

		if not self.imageBrandDict:
			url = "%s%s" % ("https://flash.hdfreaks.cc/openhdf/distros/", self.model)
			try:
				self.imageBrandDict = json.load(urlopen(url, timeout=3))
			except:
				print("[FlashImage] getImageBrandList Error: Unable to load json data from URL '%s'!" % url)
			if self.imageBrandDict:
				self.imageBrandDict.update({self.selectedImage[0]: self.selectedImage[1]})
				if len(self.imageBrandDict) > 1:
					self["key_blue"].setText(_("Other Images"))
		if not self.imagesList:
			if not self.jsonlist:
				try:
					self.jsonlist = dict(json.load(urlopen(Request(self.selectedImage[1]["url"], headers={'User-Agent': 'Mozilla/5.0'}), timeout=3)))
				except HTTPError as err:
					print("[FlashImage] getImagesList Error: Unable to load json data from URL '%s'!" % self.selectedImage[1]["url"])
					print("[FlashImage] Cause: %s" % err)
				except:
					print("[FlashImage] getImagesList Error: Unable to load json data from URL '%s'!" % self.selectedImage[1]["url"])
				alternative_imagefeed = config.usage.alternative_imagefeed.value
				if alternative_imagefeed:
					if "http" in alternative_imagefeed:
						url = "%s%s" % (config.usage.alternative_imagefeed.value, self.model)
						try:
							self.jsonlist.update(dict(json.load(urlopen(url, timeout=3))))
						except:
							print("[FlashImage] getImagesList Error: Unable to load json data from alternative URL '%s'!" % url)

			self.imagesList = dict(self.jsonlist)

			for media in ['/media/%s' % x for x in os.listdir('/media')] + (['/media/net/%s' % x for x in os.listdir('/media/net')] if os.path.isdir('/media/net') else []):
				try:
					getImages(media, [os.path.join(media, x) for x in os.listdir(media) if os.path.splitext(x)[1] == ".zip" and checkModels(x)])
					for folder in ["images", "downloaded_images", "imagebackups", "full_backups"]:
						if folder in os.listdir(media):
							subfolder = os.path.join(media, folder)
							if os.path.isdir(subfolder) and not os.path.islink(subfolder) and not os.path.ismount(subfolder):
								getImages(subfolder, [os.path.join(subfolder, x) for x in os.listdir(subfolder) if os.path.splitext(x)[1] == ".zip" and checkModels(x)])
								for dir in [dir for dir in [os.path.join(subfolder, dir) for dir in os.listdir(subfolder)] if os.path.isdir(dir) and os.path.splitext(dir)[1] == ".unzipped"]:
									shutil.rmtree(dir)
				except:
					pass

		imageList = []
		for catagorie in conditional_sort(self.imagesList.keys(), lambda w: _("Downloaded Images") not in w and _("Fullbackup Images") not in w):
			if catagorie in self.expanded:
				imageList.append(ChoiceEntryComponent('expanded', ((str(catagorie)), "Expander")))
				for image in reversed(sorted(self.imagesList[catagorie].keys())):
					imageList.append(ChoiceEntryComponent('verticalline', ((str(self.imagesList[catagorie][image]['name'])), str(self.imagesList[catagorie][image]['link']))))
			else:
				for image in self.imagesList[catagorie].keys():
					imageList.append(ChoiceEntryComponent('expandable', ((str(catagorie)), "Expander")))
					break
		if imageList:
			self["list"].setList(imageList)
			if self.setIndex:
				self["list"].moveToIndex(self.setIndex if self.setIndex < len(imageList) else len(imageList) - 1)
				if self["list"].l.getCurrentSelection()[0][1] == "Expander":
					self.setIndex -= 1
					if self.setIndex:
						self["list"].moveToIndex(self.setIndex if self.setIndex < len(imageList) else len(imageList) - 1)
				self.setIndex = 0
			self.selectionChanged()
		else:
			self["list"].setList([ChoiceEntryComponent('', ((_("Cannot find images - please try later or select an alternate image")), "Waiter"))])

	def keyOk(self):
		currentSelected = self["list"].l.getCurrentSelection()
		if currentSelected[0][1] == "Expander":
			if currentSelected[0][0] in self.expanded:
				self.expanded.remove(currentSelected[0][0])
			else:
				self.expanded.append(currentSelected[0][0])
			self.getImagesList()
		elif currentSelected[0][1] != "Waiter":
			self.session.openWithCallback(self.reloadImagesList, FlashImage, currentSelected[0][0], currentSelected[0][1])

	def reloadImagesList(self):
		self["list"].setList([ChoiceEntryComponent('', ((_("Retrieving image list - Please wait...")), "Waiter"))])
		self["list"].moveToIndex(0)
		self.selectionChanged()
		self.imagesList = {}
		self.callLater(self.getImagesList)

	def keyYellow(self):
		currentSelected = self["list"].l.getCurrentSelection()[0][1]
		if not ("://" in currentSelected or currentSelected in ["Expander", "Waiter"]):
			try:
				os.remove(currentSelected)
				currentSelected = ".".join([currentSelected[:-4], "unzipped"])
				if os.path.isdir(currentSelected):
					shutil.rmtree(currentSelected)
				self.setIndex = self["list"].getSelectedIndex()
				self.imagesList = []
				self.getImagesList()
			except:
				self.session.open(MessageBox, _("Cannot delete downloaded image"), MessageBox.TYPE_ERROR, timeout=3)
		elif BoxInfo.getItem("canKexec"):
			self.session.open(KexecInit)

	def otherImages(self):
		if len(self.imageBrandDict) > 1:
			self.session.openWithCallback(self.otherImagesCallback, ChoiceBox, list=[(key, self.imageBrandDict[key]) for key in self.imageBrandDict.keys()], windowTitle=_("Select an image brand"))

	def otherImagesCallback(self, image):
		if image:
			self.selectedImage = image
			self.jsonlist = {}
			self.expanded = []
			self.reloadImagesList()

	def selectionChanged(self):
		currentSelected = self["list"].l.getCurrentSelection()
		if "://" in currentSelected[0][1] or currentSelected[0][1] in ["Expander", "Waiter"]:
			self["key_yellow"].setText(_("Initialize Multiboot") if BoxInfo.getItem("canKexec") else "")
		else:
			self["key_yellow"].setText(_("Delete image"))
		if currentSelected[0][1] == "Waiter":
			self["key_green"].setText("")
		else:
			if currentSelected[0][1] == "Expander":
				self["key_green"].setText(_("Compress") if currentSelected[0][0] in self.expanded else _("Expand"))
				self["description"].setText("")
			else:
				self["key_green"].setText(_("Flash Image"))
				self["description"].setText(currentSelected[0][1])

	def keyLeft(self):
		self["list"].instance.moveSelection(self["list"].instance.pageUp)
		self.selectionChanged()

	def keyRight(self):
		self["list"].instance.moveSelection(self["list"].instance.pageDown)
		self.selectionChanged()

	def keyUp(self):
		self["list"].instance.moveSelection(self["list"].instance.moveUp)
		self.selectionChanged()

	def keyDown(self):
		self["list"].instance.moveSelection(self["list"].instance.moveDown)
		self.selectionChanged()


class FlashImage(Screen):
	skin = """<screen position="center,center" size="700,150" flags="wfNoBorder" backgroundColor="#54242424">
		<widget name="header" position="5,10" size="e-10,50" font="Regular;40" backgroundColor="#54242424"/>
		<widget name="info" position="5,60" size="e-10,130" font="Regular;24" backgroundColor="#54242424"/>
		<widget name="progress" position="5,e-39" size="e-10,24" backgroundColor="#54242424"/>
	</screen>"""

	BACKUP_SCRIPT = resolveFilename(SCOPE_PLUGINS, "Extensions/AutoBackup/settings-backup.sh")

	def __init__(self, session, imagename, source):
		Screen.__init__(self, session)
		self.containerbackup = None
		self.containerofgwrite = None
		self.getImageList = None
		self.downloader = None
		self.source = source
		self.imagename = imagename
		self.reasons = getReasons(session)

		self["header"] = Label(_("Backup settings"))
		self["info"] = Label(_("Save settings and EPG data"))
		self["progress"] = ProgressBar()
		self["progress"].setRange((0, 100))
		self["progress"].setValue(0)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.abort,
			"red": self.abort,
			"ok": self.ok,
			"green": self.ok,
		}, -1)

		self.callLater(self.confirmation)

	def confirmation(self):
		if self.reasons:
			self.message = _("%s\nDo you still want to flash image\n%s?") % (self.reasons, self.imagename)
		else:
			self.message = _("Do you want to flash image\n%s?") % self.imagename
		if BoxInfo.getItem("canMultiBoot"):
			self.message = _("Where do you want to flash image\n%s to?") % self.imagename
			imagesList = GetImagelist()
			currentimageslot = GetCurrentImage()
			choices = []
			slotdict = {k: v for k, v in BoxInfo.getItem("canMultiBoot").items() if not v['device'].startswith('/dev/sda')}
			for x in range(1, len(slotdict) + 1):
				choices.append(((_("slot%s - %s (current image), with backup") if x == currentimageslot else _("slot%s - %s, with backup")) % (x, imagesList[x]['imagename']), (x, "with backup")))
			for x in range(1, len(slotdict) + 1):
				choices.append(((_("slot%s - %s (current image), without backup") if x == currentimageslot else _("slot%s - %s, without backup")) % (x, imagesList[x]['imagename']), (x, "without backup")))
			if "://" in self.source:
				choices.append((_("No, only download"), (1, "only download")))
			choices.append((_("No, do not flash image"), False))
			self.session.openWithCallback(self.checkMedia, MessageBox, self.message, list=choices, default=currentimageslot, simple=True)
		else:
			choices = [(_("Yes, with backup"), "with backup"), (_("Yes, without backup"), "without backup")]
			if "://" in self.source:
				choices.append((_("No, only download"), "only download"))
			choices.append((_("No, do not flash image"), False))
			self.session.openWithCallback(self.checkMedia, MessageBox, self.message, list=choices, default=False, simple=True)

	def checkMedia(self, retval):
		if retval:
			global doBackup
			if BoxInfo.getItem("canMultiBoot"):
				global multibootslot
				multibootslot = retval[0]
				doBackup = retval[1] == "with backup"
				self.onlyDownload = retval[1] == "only download"
			else:
				doBackup = retval == "with backup"
				self.onlyDownload = retval == "only download"

			def findmedia(path):
				def avail(path):
					if not path.startswith('/mmc') and os.path.isdir(path) and os.access(path, os.W_OK):
						try:
							statvfs = os.statvfs(path)
							return (statvfs.f_bavail * statvfs.f_frsize) // (1 << 20)
						except OSError as err:
							print("[FlashImage] checkMedia Error %d: Unable to get status for '%s'! (%s)" % (err.errno, path, err.strerror))
					return 0

				def checkIfDevice(path, diskstats):
					st_dev = os.stat(path).st_dev
					return (os.major(st_dev), os.minor(st_dev)) in diskstats

				diskstats = [(int(x[0]), int(x[1])) for x in [x.split()[0:3] for x in open('/proc/diskstats').readlines()] if x[2].startswith("sd")]
				if os.path.isdir(path) and checkIfDevice(path, diskstats) and avail(path) > 500:
					return (path, True)
				mounts = []
				devices = []
				for path in ['/media/%s' % x for x in os.listdir('/media')] + (['/media/net/%s' % x for x in os.listdir('/media/net')] if os.path.isdir('/media/net') else []):
					try:
						if checkIfDevice(path, diskstats):
							devices.append((path, avail(path)))
						else:
							mounts.append((path, avail(path)))
					except OSError:
						pass
				devices.sort(key=lambda x: x[1], reverse=True)
				mounts.sort(key=lambda x: x[1], reverse=True)
				return ((devices[0][1] > 500 and (devices[0][0], True)) if devices else mounts and mounts[0][1] > 500 and (mounts[0][0], False)) or (None, None)

			global isDevice
			self.destination, isDevice = findmedia(os.path.isfile(self.BACKUP_SCRIPT) and hasattr(config.plugins, "autobackup") and config.plugins.autobackup.where.value or "/media/hdd")

			if self.destination:

				destination = os.path.join(self.destination, 'downloaded_images')
				self.zippedimage = "://" in self.source and os.path.join(destination, self.imagename) or self.source
				self.unzippedimage = os.path.join(destination, '%s.unzipped' % self.imagename[:-4])

				try:
					if os.path.isfile(destination):
						os.remove(destination)
					if not os.path.isdir(destination):
						os.mkdir(destination)
					if not self.onlyDownload:
						#self.flashPostAction()
						self.flashPostActionFirst()
					else:
						self.session.openWithCallback(self.startDownload, MessageBox, _("Starting download of image file?\nPress OK to start or Exit to abort."), type=MessageBox.TYPE_INFO, timeout=0)
				except:
					self.session.openWithCallback(self.abort, MessageBox, _("Unable to create the required directories on the media (e.g. USB stick or Harddisk) - Please verify media and try again!"), type=MessageBox.TYPE_ERROR, simple=True)
			else:
				self.session.openWithCallback(self.abort, MessageBox, _("Could not find suitable media - Please remove some downloaded images or insert a media (e.g. USB stick) with sufficiant free space and try again!"), type=MessageBox.TYPE_ERROR, simple=True)
		else:
			self.abort()

	def startBackupsettings(self, retval):
		if retval:
			self["info"].setText(_("Backing up to: %s") % self.destination)
			if retval is True:
				self["info"].setText(_("Backing up to: %s") % self.destination)
				self.session.openWithCallback(self.startDownload, BackupScreen, runBackup=True)
		else:
			self.abort()

	def startDownload(self, reply=True):
		self.show()
		if reply:
			if "://" in self.source:
				self["header"].setText(_("Downloading Image"))
				self["info"].setText(self.imagename)
				self.downloader = downloadWithProgress(self.source, self.zippedimage)
				self.downloader.addProgress(self.downloadProgress)
				self.downloader.addEnd(self.downloadEnd)
				self.downloader.addError(self.downloadError)
				self.downloader.start()
			else:
				self.unzip()
		else:
			self.abort()

	def downloadProgress(self, current, total):
		self["progress"].setValue(int(100 * current / total))

	def downloadError(self, reason):
		self.downloader.stop()
		self.session.openWithCallback(self.abort, MessageBox, _("Error during downloading image\n%s\n%s") % (self.imagename, reason), type=MessageBox.TYPE_ERROR, simple=True)

	def downloadEnd(self, filename=None):
		self.downloader.stop()
		self.unzip()

	def unzip(self):
		if self.onlyDownload:
			self.session.openWithCallback(self.abort, MessageBox, _("Download Successful\n%s") % self.imagename, type=MessageBox.TYPE_INFO, simple=True)
		else:
			self["header"].setText(_("Unzipping Image"))
			self["info"].setText("%s\n%s" % (self.imagename, _("Please wait")))
			self["progress"].hide()
			self.callLater(self.doUnzip)

	def doUnzip(self):
		try:
			zipfile.ZipFile(self.zippedimage, 'r').extractall(self.unzippedimage)
			self.flashimage()
		except:
			self.session.openWithCallback(self.abort, MessageBox, _("Error during unzipping image\n%s") % self.imagename, type=MessageBox.TYPE_ERROR, simple=True)

	def flashimage(self):
		self["header"].setText(_("Flashing Image"))

		def findimagefiles(path):
			for path, subdirs, files in os.walk(path):
				if not subdirs and files:
					return checkimagefiles(files) and path
		imagefiles = findimagefiles(self.unzippedimage)
		if imagefiles:
			if BoxInfo.getItem("canMultiBoot"):
				global multibootslot
				command = "/usr/bin/ofgwrite -k -r -m%s '%s'" % (multibootslot, imagefiles)
			else:
				command = "/usr/bin/ofgwrite -k -r '%s'" % imagefiles
			self.createSkinRestoreFile()
			self.containerofgwrite = Console()
			self.containerofgwrite.ePopen(command, self.FlashimageDone)
		else:
			self.session.openWithCallback(self.abort, MessageBox, _("Image to install is invalid\n%s") % self.imagename, type=MessageBox.TYPE_ERROR, simple=True)

	def createSkinRestoreFile(self):
		try:
			skinrestorefile = "/media/hdd/images/skinrestore"
			if fileExists(skinrestorefile):
				print("[SkinRestore]: Skinrestorefile exists")
			else:
				open(skinrestorefile, 'a').close()
				print("[SkinRestore]: Skinrestorefile created")
		except:
			pass

	def FlashimageDone(self, data, retval, extra_args):
		self.containerofgwrite = None
		if retval == 0:
			self["header"].setText(_("Flashing image successful"))
			if BoxInfo.getItem("canMultiBoot"):
				self.restore()
			self["info"].setText(_("%s\nPress ok for multiboot selection\nPress exit to close") % self.imagename)
		else:
			self.session.openWithCallback(self.abort, MessageBox, _("Flashing image was not successful\n%s") % self.imagename, type=MessageBox.TYPE_ERROR, simple=True)

	def abort(self, reply=None):
		if self.getImageList or self.containerofgwrite:
			return 0
		if self.downloader:
			self.downloader.stop()
		if self.containerbackup:
			self.containerbackup.killAll()
		self.close()

	def ok(self):
		if self["header"].text == _("Flashing image successful"):
			self.session.openWithCallback(self.abort, MultibootSelection)
		else:
			return 0

	def restore(self):
		global multibootslot
		# mount point
		self.tmp_dir = tempfile.mkdtemp(prefix="MultibootSelection")
		# Actual data directory (differs in case of rootsubdir)
		self.image_dir = os.sep.join(filter(None, [self.tmp_dir, BoxInfo.getItem("canMultiBoot")[multibootslot].get('rootsubdir', '')]))
		if os.path.exists("/media/hdd/images/config/settings"):
			Console().ePopen('mount %s %s' % (BoxInfo.getItem("canMultiBoot")[multibootslot]['device'], self.tmp_dir))
			self.restore_settings(self.tmp_dir, self.image_dir)

	def restore_settings(self, tmpdir, image_dir):
		filename = "%s/%s" % (getBackupPath(), getBackupFilename())
		self.session.openWithCallback(self.cleanUp, RestoreScreen, runRestore=True, restorePath=tmpdir, image_dir=image_dir)

	def cleanUp(self):
		Console().ePopen('umount %s' % self.tmp_dir)
		Console().ePopen('rm /tmp/chroot.sh /tmp/groups.txt /tmp/groups.txt /tmp/installed-list.txt self.tmp_dir')

	def flashPostActionFirst(self):
		backupfilename = "%s/%s" % (getBackupPath(), getBackupFilename())
		if fileExists(backupfilename):
			self.flashPostAction()
		else:
			self.flashPostAction2()

	def flashPostAction(self, retVal=True):
		if retVal:
			self.recordCheck = False
			text = _("What should be restored?\n")
			if getImageDistro() in self.imagename:
				if os.path.exists("/media/hdd/images/config/myrestore.sh"):
					text = "%s\n%s" % (text, _("(The file '/media/hdd/images/config/myrestore.sh' exists and will be run after the image is flashed.)"))
				choices = [
					(_("Everything"), "restoresettingsandallplugins"),
					(_("Nothing"), "wizard"),
					(_("Settings without plugins"), "restoresettingsnoplugin"),
					(_("Settings and selected plugins"), "restoresettings"),
					(_("Do not flash image"), "abort")
				]
				default = self.selectPrevPostFlashAction()
				if "backup" in self.imagename:
					text = _("Flash Backupimage")
					text = "%s\n%s?" % (text, self.imagename)
					choices = [
						(_("Yes"), "nothing"),
						(_("Do not flash image"), "abort")
					]
					default = 0
			else:
				text = _("Flash Image")
				text = "%s\n%s?" % (text, self.imagename)
				choices = [
					(_("Yes"), "wizard"),
					(_("Do not flash image"), "abort")
				]
				default = 0
			self.session.openWithCallback(self.postFlashActionCallback, MessageBox, text, list=choices, default=default, simple=True)
		else:
			self.abort()

	def flashPostAction2(self, retVal=True):
		if retVal:
			self.recordCheck = False
			text = _("What should be restored?\nNo saved settings found!")
			if getImageDistro() in self.imagename:
				if os.path.exists("/media/hdd/images/config/myrestore.sh"):
					text = "%s\n%s" % (text, _("(The file '/media/hdd/images/config/myrestore.sh' exists and will be run after the image is flashed.)"))
				choices = [
					(_("Nothing"), "wizard"),
					(_("Do not flash image"), "abort")
				]
				default = self.selectPrevPostFlashAction()
				if "backup" in self.imagename:
					text = _("Flash Backupimage")
					text = "%s\n%s?" % (text, self.imagename)
					choices = [
						(_("Yes"), "nothing"),
						(_("Do not flash image"), "abort")
					]
					default = 0
			else:
				text = _("Flash Image")
				text = "%s\n%s?" % (text, self.imagename)
				choices = [
					(_("Yes"), "wizard"),
					(_("Do not flash image"), "abort")
				]
				default = 0
			self.session.openWithCallback(self.postFlashActionCallback, MessageBox, text, list=choices, default=default, simple=True)
		else:
			self.abort()

	def selectPrevPostFlashAction(self):
		index = 1
		if os.path.exists("/media/hdd/images/config/settings"):
			index = 3
			if os.path.exists("/media/hdd/images/config/noplugins"):
				index = 2
			if os.path.exists("/media/hdd/images/config/plugins"):
				index = 0
		return index

	def postFlashActionCallback(self, choice):
		global doBackup
		if choice:
			rootFolder = "/media/hdd/images/config"
			if choice != "abort" and not self.recordCheck:
				self.recordCheck = True
				recording = self.session.nav.RecordTimer.isRecording()
				nextRecordingTime = self.session.nav.RecordTimer.getNextRecordingTime()
				if recording or (nextRecordingTime > 0 and (nextRecordingTime - time.time()) < 360):
					self.choice = choice
					self.session.openWithCallback(self.recordWarningCallback, MessageBox, "%s\n\n%s" % (_("Recording(s) are in progress or coming up in few seconds!"), _("Flash your %s %s and reboot now?") % (getMachineBrand(), getMachineName())), default=False)
					return
			restoreSettings = ("restoresettings" in choice)
			restoreSettingsnoPlugin = (choice == "restoresettingsnoplugin")
			restoreAllPlugins = (choice == "restoresettingsandallplugins")
			if restoreSettings and doBackup:
				self.saveEPG()
			if choice != "abort":
				filesToCreate = []
				try:
					if not os.path.exists(rootFolder):
						os.makedirs(rootFolder)
				except OSError as err:
					print("[FlashImage] postFlashActionCallback Error %d: Failed to create '%s' folder!  (%s)" % (err.errno, rootFolder, err.strerror))
				if restoreSettings:
					filesToCreate.append("settings")
				if restoreAllPlugins:
					filesToCreate.append("plugins")
				if restoreSettingsnoPlugin:
					filesToCreate.append("noplugins")
				for fileName in ["settings", "plugins", "noplugins"]:
					path = os.path.join(rootFolder, fileName)
					if fileName in filesToCreate:
						try:
							open(path, "w").close()
						except OSError as err:
							print("[FlashImage] postFlashActionCallback Error %d: failed to create %s! (%s)" % (err.errno, path, err.strerror))
					else:
						if os.path.exists(path):
							os.unlink(path)
				global isDevice
				if doBackup:
					if isDevice:
						self.startBackupsettings(True)
					else:
						self.session.openWithCallback(self.startBackupsettings, MessageBox, _("Can only find a network drive to store the backup this means after the flash the autorestore will not work. Alternativaly you can mount the network drive after the flash and perform a manufacurer reset to autorestore"), simple=True)
				else:
					self.startDownload()
			else:
				self.abort()
		else:
			self.abort()

	def saveEPG(self):
		epgCache = eEPGCache.getInstance()
		epgCache.save()

	def recordWarningCallback(self, choice):
		if not choice:
			self.abort()
			return

		self.postFlashActionCallback(self.choice)


class MultibootSelection(SelectImage):
	skin = """<screen name="SelectImage" position="center,center" size="560,440" title="SoftwareManager setup">
		<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget name="list" position="5,50" size="550,350" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="div-h.png" position="0,400" zPosition="1" size="560,2" />
		<widget source="descripion" render="Label" position="5,410" size="550,30" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />
	</screen>"""

	def __init__(self, session, *args):
		SelectImage.__init__(self, session)
		self.skinName = ["MultibootSelection", "SelectImage"]
		self.expanded = []
		self.tmp_dir = None
		self.setTitle(_("Multiboot image selector"))
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Reboot"))
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()
		self["description"] = Label()
		self["list"] = ChoiceList([])

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "KeyboardInputActions", "MenuActions"],
		{
			"ok": self.keyOk,
			"cancel": self.cancel,
			"red": self.cancel,
			"green": self.keyOk,
			"yellow": self.deleteImage,
			"blue": self.order,
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
			"upRepeated": self.keyUp,
			"downRepeated": self.keyDown,
			"leftRepeated": self.keyLeft,
			"rightRepeated": self.keyRight,
			"menu": boundFunction(self.cancel, True),
		}, -1)

		self.blue = False
		self.currentimageslot = GetCurrentImage()
		self.tmp_dir = tempfile.mkdtemp(prefix="MultibootSelection")
		Console().ePopen('mount %s %s' % (BoxInfo.getItem("MultibootStartupDevice"), self.tmp_dir))
		self.getImagesList()

	def cancel(self, value=None):
		Console().ePopen('umount %s' % self.tmp_dir)
		if not os.path.ismount(self.tmp_dir):
			os.rmdir(self.tmp_dir)
		if value == 2:
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close(value)

	def getImagesList(self):
		list = []
		list12 = []
		imagesList = GetImagelist()
		mode = GetCurrentImageMode() or 0
		self.deletedImagesExists = False
		if imagesList:
			for index, x in enumerate(imagesList):
				if imagesList[x]["imagename"] == _("Deleted image"):
					self.deletedImagesExists = True
				elif imagesList[x]["imagename"] != _("Empty slot"):
					if BoxInfo.getItem("canMode12"):
						list.insert(index, ChoiceEntryComponent('', ((_("slot%s - %s mode 1 (current image)") if x == self.currentimageslot and mode != 12 else _("slot%s - %s mode 1")) % (x, imagesList[x]['imagename']), (x, 1))))
						list12.insert(index, ChoiceEntryComponent('', ((_("slot%s - %s mode 12 (current image)") if x == self.currentimageslot and mode == 12 else _("slot%s - %s mode 12")) % (x, imagesList[x]['imagename']), (x, 12))))
					else:
						list.append(ChoiceEntryComponent('', ((_("slot%s - %s (current image)") if x == self.currentimageslot and mode != 12 else _("slot%s - %s")) % (x, imagesList[x]['imagename']), (x, 1))))

		if list12:
			self.blue = True
			self["key_blue"].setText(_("Order by modes") if config.usage.multiboot_order.value else _("Order by slots"))
			list += list12
			list = sorted(list) if config.usage.multiboot_order.value else list

		if os.path.isfile(os.path.join(self.tmp_dir, "STARTUP_RECOVERY")):
			if BoxInfo.getItem("hasKexec"):
				recovery_booted = fileHas("/proc/cmdline", "rootsubdir=linuxrootfs0")
				self["description"].setText(_("Attention - forced loading recovery image!\nCreate an empty STARTUP_RECOVERY file at the root of your HDD/USB drive and hold the Power button for more than 12 seconds for reboot receiver!"))
				list.append(ChoiceEntryComponent('', (_("Boot to Recovery image - slot0 %s") % (recovery_booted and _("(current image)") or ""), "Recovery")))
			else:
				list.append(ChoiceEntryComponent('', (_("Boot to Recovery menu"), "Recovery")))
		if os.path.isfile(os.path.join(self.tmp_dir, "STARTUP_ANDROID")):
			list.append(ChoiceEntryComponent('', ((_("Boot to Android image")), "Android")))
		if not list:
			list.append(ChoiceEntryComponent('', ((_("No images found")), "Waiter")))
		self["list"].setList(list)
		for index, slot in enumerate(list):
			if type(slot[0][1]) is tuple and self.currentimageslot == slot[0][1][0] and (not BoxInfo.getItem("canMode12") or mode == slot[0][1][1]) or BoxInfo.getItem("hasKexec") and slot[0][1] == "Recovery" and recovery_booted:
				self["list"].moveToIndex(index)
				break
		self.selectionChanged()

	def deleteImage(self):
		if self["key_yellow"].text == _("Restore deleted images"):
			self.session.openWithCallback(self.deleteImageCallback, MessageBox, _("Are you sure to restore all deleted images"), simple=True)
		elif self["key_yellow"].text == _("Delete Image"):
			self.session.openWithCallback(self.deleteImageCallback, MessageBox, "%s:\n%s" % (_("Are you sure to delete image"), self.currentSelected[0][0]), simple=True)

	def deleteImageCallback(self, answer):
		if answer:
			if self["key_yellow"].text == _("Restore deleted images"):
				restoreImages()
			else:
				deleteImage(self.currentSelected[0][1][0])
			self.getImagesList()

	def order(self):
		if self.blue:
			self["list"].setList([])
			config.usage.multiboot_order.value = not config.usage.multiboot_order.value
			config.usage.multiboot_order.save()
			self.getImagesList()

	def keyOk(self):
		self.session.openWithCallback(self.doReboot, MessageBox, "%s:\n%s" % (_("Are you sure to reboot to"), self.currentSelected[0][0]), simple=True)

	def doReboot(self, answer):
		if answer:
			slot = self.currentSelected[0][1]
			if slot == "Recovery":
				shutil.copyfile(os.path.join(self.tmp_dir, "STARTUP_RECOVERY"), os.path.join(self.tmp_dir, "STARTUP"))
			elif slot == "Android":
				shutil.copyfile(os.path.join(self.tmp_dir, "STARTUP_ANDROID"), os.path.join(self.tmp_dir, "STARTUP"))
			elif BoxInfo.getItem("canMultiBoot")[slot[0]]['startupfile']:
				if BoxInfo.getItem("canMode12"):
					startupfile = os.path.join(self.tmp_dir, "%s_%s" % (BoxInfo.getItem("canMultiBoot")[slot[0]]['startupfile'].rsplit('_', 1)[0], slot[1]))
				else:
					startupfile = os.path.join(self.tmp_dir, "%s" % BoxInfo.getItem("canMultiBoot")[slot[0]]['startupfile'])
				if BoxInfo.getItem("canDualBoot"):
					with open('/dev/block/by-name/flag', 'wb') as f:
						f.write(struct.pack("B", int(slot[0])))
					startupfile = os.path.join("/boot", "%s" % BoxInfo.getItem("canMultiBoot")[slot[0]]['startupfile'])
					shutil.copyfile(startupfile, os.path.join("/boot", "STARTUP"))
				else:
					shutil.copyfile(startupfile, os.path.join(self.tmp_dir, "STARTUP"))
			else:
				model = HardwareInfo().get_machine_name()
				if slot[1] == 1:
					startupFileContents = "boot emmcflash0.kernel%s 'root=/dev/mmcblk0p%s rw rootwait %s_4.boxmode=1'\n" % (slot[0], slot[0] * 2 + 1, model)
				else:
					startupFileContents = "boot emmcflash0.kernel%s 'brcm_cma=520M@248M brcm_cma=%s@768M root=/dev/mmcblk0p%s rw rootwait %s_4.boxmode=12'\n" % (slot[0], BoxInfo.getItem("canMode12"), slot[0] * 2 + 1, model)
				open(os.path.join(self.tmp_dir, "STARTUP"), 'w').write(startupFileContents)
			self.cancel(2)

	def selectionChanged(self):
		self.currentSelected = self["list"].l.getCurrentSelection()
		if isinstance(self.currentSelected[0][1], tuple) and self.currentimageslot != self.currentSelected[0][1][0]:
			self["key_yellow"].setText(_("Delete Image"))
		elif self.deletedImagesExists:
			self["key_yellow"].setText(_("Restore deleted images"))
		else:
			self["key_yellow"].setText("")


class KexecInit(Screen):
	def __init__(self, session, *args):
		Screen.__init__(self, session)
		self.skinName = ["KexecInit", "Setup"]
		self.setTitle(_("Kexec MultiBoot Manager"))
		self.kexec_files = fileExists("/usr/bin/kernel_auto.bin") and fileExists("/usr/bin/STARTUP.cpio.gz")
		self["description"] = Label(_("Press Green key to enable MultiBoot!\n\nWill reboot within 10 seconds,\nunless you have eMMC slots to restore.\nRestoring eMMC slots can take from 1 -> 5 minutes per slot."))
		self["key_red"] = StaticText(self.kexec_files and _("Remove forever") or "")
		self["key_green"] = StaticText(_("Init"))
		self["actions"] = ActionMap(["TeletextActions"],
		{
			"green": self.RootInit,
			"ok": self.close,
			"exit": self.close,
			"red": self.removeFiles,
		}, -1)

	def RootInit(self):
		self["actions"].setEnabled(False)  # This function takes time so disable the ActionMap to avoid responding to multiple button presses
		if self.kexec_files:
			modelMtdRootKernel = BoxInfo.getItem("canKexec")
			self.setTitle(_("Kexec MultiBoot Initialisation - will reboot after 10 seconds."))
			self["description"].setText(_("Kexec MultiBoot Initialisation in progress!\n\nWill reboot after restoring any eMMC slots.\nThis can take from 1 -> 5 minutes per slot."))
			open("/STARTUP", 'w').write("kernel=/zImage root=/dev/%s rootsubdir=linuxrootfs0" % modelMtdRootKernel[0])
			open("/STARTUP_RECOVERY", 'w').write("kernel=/zImage root=/dev/%s rootsubdir=linuxrootfs0" % modelMtdRootKernel[0])
			open("/STARTUP_1", 'w').write("kernel=/linuxrootfs1/zImage root=/dev/%s rootsubdir=linuxrootfs1" % modelMtdRootKernel[0])
			open("/STARTUP_2", 'w').write("kernel=/linuxrootfs2/zImage root=/dev/%s rootsubdir=linuxrootfs2" % modelMtdRootKernel[0])
			open("/STARTUP_3", 'w').write("kernel=/linuxrootfs3/zImage root=/dev/%s rootsubdir=linuxrootfs3" % modelMtdRootKernel[0])
			cmdlist = []
			cmdlist.append("dd if=/dev/%s of=/zImage" % modelMtdRootKernel[1])  # backup old kernel
			cmdlist.append("dd if=/usr/bin/kernel_auto.bin of=/dev/%s" % modelMtdRootKernel[1])  # create new kernel
			cmdlist.append("mv /usr/bin/STARTUP.cpio.gz /STARTUP.cpio.gz")  # copy userroot routine
			Console().eBatch(cmdlist, self.RootInitEnd, debug=True)
		else:
			self.session.open(MessageBox, _("Unable to complete - Kexec Multiboot files missing!"), MessageBox.TYPE_INFO, timeout=10)
			self.close()

	def RootInitEnd(self, *args, **kwargs):
		from Screens.Standby import TryQuitMainloop
		model = HardwareInfo().get_machine_name()
		for usbslot in range(1, 4):
			if pathExists("/media/hdd/%s/linuxrootfs%s" % (model, usbslot)):
				Console().ePopen("cp -R /media/hdd/%s/linuxrootfs%s . /" % (model, usbslot))
		self.session.open(TryQuitMainloop, 2)

	def removeFiles(self):
		if self.kexec_files:
			self.session.openWithCallback(self.removeFilesAnswer, MessageBox, _("Really permanently delete MultiBoot files?\n%s") % "(/usr/bin/kernel_auto.bin /usr/bin/STARTUP.cpio.gz)", simple=True)

	def removeFilesAnswer(self, answer=None):
		if answer:
			Console().ePopen("rm -rf /usr/bin/kernel_auto.bin /usr/bin/STARTUP.cpio.gz")
			self.close()
