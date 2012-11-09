from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.Sources.StaticText import StaticText
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.PluginList import *
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Downloader import downloadWithProgress
from enigma import ePicLoad, eTimer
from twisted.web.client import downloadPage
import os
import sys

#check the boxtype#
menulog = open("/proc/cpuinfo", "r")
for line in menulog:
    if "BCM7413B1 STB platform" in line:
        box = "et9000"
        boxname = "ET9x00/ET6x00"
    elif "STx7111" in line:
        box = "spark"
        boxname = "Spark"
    elif "STx7105" in line:
        box = "spark"
        boxname = "Spark"
    elif "BCM7335B0 STB platform" in line:
        box = "vuduo"
        boxname = "Vu+Duo"
    elif "NXP STB22x" in line:
        box = "tm800"
        boxname = "TM800"
    elif "STx7109" in line:
        box = "ipbox"
        boxname = "IPBox"
    elif os.path.exists("/proc/stb/info/gbmodel"): 
        if open("/proc/stb/info/gbmodel",'r').read().strip() == "quad":
            box = "gbquad"
            boxname = "GigaBlue"
    elif os.path.exists("/proc/stb/info/gbmodel"):
        if open("/proc/stb/info/model",'r').read().strip() == "Gigablue":
            box = "gigablue"
            boxname = "GigaBlue"
    elif "BCM7325B0 STB platform" and "220.16" in line:
        box = "vusolo"
        boxname = "Vu+Solo"
    elif "AMD Phenom(tm) II X6 1090T Processor" in line:
        box = "et9000"
        boxname = "Henry VM"
    elif "BCM97xxx Settop Platform" in line:
        if open("/proc/stb/info/boxtype",'r').read().strip() == "Ixuss One":
            box = "et9000"
            boxname = "Ixuss One"
        if open("/proc/stb/info/boxtype",'r').read().strip() == "Zuron One":
            box = "et9000"
            boxname = "Zuron One"
if os.path.exists("/proc/stb/info/hwmodel"):
    if open("/proc/stb/info/hwmodel",'r').read().strip() == "twin":
        box = "tmtwin"
        boxname = "TM-Twin"
menulog.close()


if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/downloader.py"):
    os.remove("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/downloader.py")
else:
    pass

if os.path.exists("/usr/bin/ipkg"):
    pass
else:
   os.system("ln -s /usr/bin/opkg-cl /usr/bin/ipkg")
   os.system("ln -s /usr/bin/opkg-cl /usr/bin/ipkg-cl")

class Hdf_Downloader(Screen):
    skin = """
          <screen name="DownloadMenu" position="center,center" size="800,400" title="Select your Download">
                <widget name="downloadmenu" position="10,10" size="400,300" scrollbarMode="showOnDemand" />
                <ePixmap name="white" position="420,15" zPosition="10" size="2,300" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/whiter.png" transparent="0" alphatest="on" />
                <ePixmap name="1" position="760,225" zPosition="1" size="40,40" pixmap="skin_default/buttons/key_1.png" transparent="1" alphatest="on" />
                <widget name="key_1" position="655,227" zPosition="2" size="100,30" valign="right" halign="right" font="Regular;15" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <ePixmap name="2" position="760,250" zPosition="1" size="40,40" pixmap="skin_default/buttons/key_2.png" transparent="1" alphatest="on" />
                <widget name="key_2" position="655,252" zPosition="2" size="100,30" valign="right" halign="right" font="Regular;15" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <ePixmap name="3" position="760,275" zPosition="1" size="40,40" pixmap="skin_default/buttons/key_3.png" transparent="1" alphatest="on" />
                <widget name="key_3" position="655,277" zPosition="2" size="100,30" valign="right" halign="right" font="Regular;15" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <ePixmap name="4" position="760,300" zPosition="1" size="40,40" pixmap="skin_default/buttons/key_4.png" transparent="1" alphatest="on" />
                <widget name="key_4" position="655,302" zPosition="2" size="100,30" valign="right" halign="right" font="Regular;15" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <ePixmap name="5" position="760,325" zPosition="1" size="40,40" pixmap="skin_default/buttons/key_5.png" transparent="1" alphatest="on" />
                <widget name="key_5" position="655,327" zPosition="2" size="100,30" valign="right" halign="right" font="Regular;15" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <ePixmap name="6" position="760,350" zPosition="1" size="40,40" pixmap="skin_default/buttons/key_6.png" transparent="1" alphatest="on" />
                <widget name="key_6" position="555,352" zPosition="2" size="200,30" valign="right" halign="right" font="Regular;15" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <ePixmap name="0" position="760,375" zPosition="1" size="40,40" pixmap="skin_default/buttons/key_0.png" transparent="1" alphatest="on" />
                <widget name="key_0" position="655,377" zPosition="2" size="100,30" valign="right" halign="right" font="Regular;15" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <ePixmap name="red" position="30,320" zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                <ePixmap name="green" position="200,320" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                <widget name="blue" position="370,320" zPosition="1" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
                <widget name="key_red" position="30,320" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green" position="200,320" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_blue" position="370,320" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <widget source="introduction" render="Label" position="0,370" size="560,30" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />
                <widget source="size" render="Label" position="500,15" size="100,30" zPosition="10" font="Regular;15" halign="left" valign="top" backgroundColor="#25062748" transparent="1" />
                <widget source="size2" render="Label" position="430,10" size="100,30" zPosition="10" font="Regular;21" halign="left" valign="top" backgroundColor="#25062748" transparent="1" />
                <widget source="description" render="Label" position="450,80" size="330,150" zPosition="10" font="Regular;15" halign="left" valign="top" backgroundColor="#25062748" transparent="1" />
                <widget source="description2" render="Label" position="430,50" size="150,30" zPosition="10" font="Regular;21" halign="left" valign="top" backgroundColor="#25062748" transparent="1" />
          </screen>"""
    
    def __init__(self, session , **kwargs):
        self.session = session
##### Variables and lists
        self.box = box
        self.anyNewInstalled = False
        self.switch = "extensions"
        self.filesArray = []
        self.filesArrayClean = []
        self.filesArraySplit = []
        self.list = []
##### Download Source File
        import urllib
        urllib.urlretrieve ("http://addons.hdfreaks.cc/feeds/down.hdf", "/tmp/.down.hdf")
##### Lets Start
        self.readSource()
        self.makeMenu()
        Screen.__init__(self, session)
        self["downloadmenu"] = MenuList(self.list)
        self["introduction"] = StaticText(_("Press OK to install the file."))
        self["size2"] = StaticText(_("Size:"))
        self["description2"] = StaticText(_("Description:"))
        self["actions"] = ActionMap(["WizardActions", "InputActions", "EPGSelectActions", "ColorActions"],
        {
            "ok" : self.ok,
            "1" : self.one,
            "2" : self.two,
            "3" : self.three,
            "4" : self.four,
            "5" : self.five,
            "6" : self.six,
            "0" : self.zero,
            "back": self.cancel,
            "blue": self.preview,
            "info": self.info,
            "menu": self.recompile,
            "red": self.cancel,
            "green": self.ok,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -1)
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Download"))
        self["key_blue"] = Label(_(" "))
        self["key_1"] = Label(_("   Plugins"))
        self["key_2"] = Label(_("   Updates"))
        self["key_3"] = Label(_("   Softcams"))
        self["key_4"] = Label(_("   Skins"))
        self["key_5"] = Label(_("   Picons"))
        self["key_6"] = Label(_("   ipk, tar.gz, tgz Installer"))
        self["key_0"] = Label(_("   Uninstaller"))
        self["size"] = StaticText(_(" "))
        self["description"] = StaticText(_(" "))
        self["blue"] = Pixmap()
        self["blue"].hide()
        self.loadInfo()

##### Reading of files
    
    def readSource(self):
        sourceread = open("/tmp/.down.hdf", "r")
        for lines in sourceread.readlines():
            if lines.split('#')[0] == "":
                pass
            else:
                newLines = lines.split('#')
                self.filesArrayClean.append(newLines[1])
                self.filesArraySplit.append(lines.split('#'))
                self.filesArray.append(newLines[1].split('-'))
        
        sourceread.close()
        os.system("rm -rf /tmp/.down.hdf")

##### Building Menu
    
    def makeMenu(self):
        
        # TMP Install:
        # 3 Werte werden benoetigt 1. Dateiname
        i = 0
        if self.switch == "tmpinst":
            tmpInstFilesArray = os.listdir("/tmp/")
            while i < len(tmpInstFilesArray):
                if "ipk" in tmpInstFilesArray[i].split(".") or "tar" in tmpInstFilesArray[i].split(".") or "tgz" in tmpInstFilesArray[i].split("."):
                    self.list.append((_(tmpInstFilesArray[i]), "tmpinst"))
                i = i + 1
        # Uninstall:
        # 3 Werte werden benoetigt 1. Name 2. Dateiname 3. uninstall
        i = 0
        if self.switch == "uninstall":
            uninstFilesArray = sorted(os.listdir("/usr/uninstall"))
            while i < len(uninstFilesArray):
                if uninstFilesArray[i].split('_')[0] == "hdf":
                    self.list.append((_(uninstFilesArray[i].split('_')[1].split('.')[0]), uninstFilesArray[i], "uninstall"))
                i = i + 1
        # Download:
        # 4 Werte werden benoetigt 1. Name 2. Dateiname 3. Groesse 4. Description 5. download (wichtig bei def ok)
        i = 0
        while i < len(self.filesArray):
            if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.devdown"):
                if self.switch in self.filesArray[i] or self.switch + "s" in self.filesArray[i] or self.switch + "shd" in self.filesArray[i]:
                    if self.switch == "extensions":
                        self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "skin":
                        self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "update":
                        self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "softcam":
                        self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "picon":
                        self.list.append((_(self.filesArray[i][2].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
            elif self.box in self.filesArraySplit[i][0]:
                if self.switch in self.filesArray[i] or self.switch + "s" in self.filesArray[i] or self.switch + "shd" in self.filesArray[i]:
                    if self.switch == "extensions":
                        if "2.7" in sys.version:
                            if "mips32el" in self.filesArrayClean[i] or "_all" in self.filesArrayClean[i]:
                                self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                        else:
                            self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "skin":
                        self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "update":
                        self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "softcam":
                        self.list.append((_(self.filesArray[i][3].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))
                    if self.switch == "picon":
                        self.list.append((_(self.filesArray[i][2].split('.')[0]), self.filesArrayClean[i] , "" + self.filesArraySplit[i][2] + "", "" + self.filesArraySplit[i][3] + "", "download"))

            i = i + 1
        self.list.append((_(" "), "none"))
    
    def delMenu(self):
        count = 0
        while len(self.list) > count:
            self.list.pop()
    
    def mkNewMenu(self):
        self.delMenu()
        self.makeMenu()
        self["downloadmenu"].moveToIndex(0)
        self.loadInfo()
        Screen.hide(self)
        Screen.show(self)

##### Onscreen Actions
    
    def loadInfo(self):
        self["blue"].hide()
        self["key_blue"].setText(" ")
        if "download" in self["downloadmenu"].l.getCurrentSelection():
            if self.switch == "skin" or self.switch == "picon":
                        self["blue"].show()
                        self["key_blue"].setText("Preview")
            self["key_green"].setText("Download")
            self["introduction"].setText("Press OK to install the file.")
            self["description"].setText(self["downloadmenu"].l.getCurrentSelection()[3])
            self["description2"].setText("Description: ")
            self["size"].setText(self["downloadmenu"].l.getCurrentSelection()[2])
            self["size2"].setText("Size: ")
            Screen.setTitle(self, "Select your Download")
        elif "uninstall" in self["downloadmenu"].l.getCurrentSelection():
            self["key_green"].setText("Remove")
            self["introduction"].setText("Press OK to remove the file.")
            self["description"].setText(" ")
            self["description2"].setText(" ")
            self["size"].setText(" ")
            self["size2"].setText(" ")
            Screen.setTitle(self, "Select your Removal")
        elif "tmpinst" in self["downloadmenu"].l.getCurrentSelection():
            self["key_green"].setText("Install")
            self["introduction"].setText("Press OK to install the file.")
            self["description"].setText(" ")
            self["description2"].setText(" ")
            self["size"].setText(" ")
            self["size2"].setText(" ")
            Screen.setTitle(self, "Select your local file to install")
        elif "cancel" or "none" in self["downloadmenu"].l.getCurrentSelection():
            self["key_green"].setText("Ok")
            self["introduction"].setText(" ")
            self["description"].setText("Press OK to do nothing")
            self["description2"].setText("Description: ")
            self["size"].setText("0")
            self["size2"].setText("Size: ")
            Screen.setTitle(self, "HDFreaks.cc Downloader")
        else:
            self["description"].setText(" ")
            self["size"].setText(" ")
        
        Screen.hide(self)
        Screen.show(self)

##### Executive Functions
    
    def restartGUI(self, answer):
        if answer is True:
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self.close()
            #self.session.open(TryQuitMainloop, 3)
        else:
            self.close()
    
    def uninstall(self, answer):
        if answer is True:
            os.chmod("/usr/uninstall/" + self["downloadmenu"].l.getCurrentSelection()[1], 755)
            os.system("sh /usr/uninstall/" + self["downloadmenu"].l.getCurrentSelection()[1] + "")
            self.anyNewInstalled = True
            Screen.hide(self)
            self.mkNewMenu()
            self.session.open(MessageBox, ("It's recommented to restart box for changes taking place!"), MessageBox.TYPE_INFO, timeout=10).setTitle(_("Uninstall complete"))
        else:
            self.close()
    
    def preview(self):
        if self.switch == "skin" or self.switch == "picon":
            file = self["downloadmenu"].l.getCurrentSelection()[1].split(".")[0] + ".jpg"
            url = "http://addons.hdfreaks.cc/feeds/" + file
            path = "/tmp/" + file
            import urllib
            print urllib.urlretrieve (url , path)
            if "<title>404 Not Found</title>" in open(path, "r").read():
                self.session.open(MessageBox, ("Sorry, no Preview available."), MessageBox.TYPE_ERROR).setTitle(_("No Preview"))
            else:
                self.session.open(PictureScreen, picPath=path)
        else:
            pass

    def recompile(self):
        if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.devdown"): 
            print "Starting Recompile"
            self.restartGUI(True)
        else:
            pass

###### Easter Egg
    
    def info(self):
        self.session.open(MessageBox, ("(c) HDF 2012\nSpecial thanks to koivo for testing\nGoogle for amounts of questions\nand\nTBX for telling me what Google couldn't"), MessageBox.TYPE_INFO, timeout=10).setTitle(_("HDFreaks.cc Downloader Info"))

###### Special Controls
    
    def ok(self):
        if "download" in self["downloadmenu"].l.getCurrentSelection():
            file = self["downloadmenu"].l.getCurrentSelection()[1]
            url = "http://addons.hdfreaks.cc/feeds/" + file
            path = "/tmp/" + file
            self.session.open(downloadfile, path, url)
            self.anyNewInstalled = True

#            os.remove(path)
        elif "tmpinst" in self["downloadmenu"].l.getCurrentSelection():
            file = self["downloadmenu"].l.getCurrentSelection()[0]
            filetype = file.split(".")[1]
            i = 1
            while i < len(file.split(".")):
                filetype = file.split(".")[i]
                if file.split(".")[i] != "ipk" or file.split(".")[i] != "tar" or file.split(".")[i] != "tgz":
                    i = i + 1
            if filetype == "ipk":
                com = "opkg install /tmp/" + file + ""
            else:
                com = "tar xzvf /tmp/" + file + " -C /"
            self.session.open(Console,_("Install Log: %s") % (com), ["%s" %com])
        elif "uninstall" in self["downloadmenu"].l.getCurrentSelection():
            self.session.openWithCallback(self.uninstall, MessageBox, _("Do you want to uninstall the Plugin?"), MessageBox.TYPE_YESNO).setTitle(_("Uninstall?"))
        else:
            returnValue = "self." + self["downloadmenu"].l.getCurrentSelection()[1] + "()"
            eval(returnValue)
    
    def cancel(self):
        if self.anyNewInstalled is True:
            self.session.openWithCallback(self.restartGUI, MessageBox, _("Activate and reload the new installed Plugins now? \n\nNo Enigma GUI Restart needed!"), MessageBox.TYPE_YESNO).setTitle(_("Reload Plugins now?"))
        else:
            self.close()
    
    def none(self):
        pass

###### Category Controls
    
    def one(self):
        self.switch = "extensions"
        self.mkNewMenu()
    
    def two(self):
        self.switch = "update"
        self.mkNewMenu()
    
    def three(self):
        self.switch = "softcam"
        self.mkNewMenu()
    
    def four(self):
        self.switch = "skin"
        self.mkNewMenu()
    
    def five(self):
        self.switch = "picon"
        self.mkNewMenu()
    
    def six(self):
        self.switch = "tmpinst"
        self.mkNewMenu()
	
    def zero(self):
        if os.path.exists("/usr/uninstall") == False:
            os.system("mkdir /usr/uninstall")
        self.switch = "uninstall"
        self.mkNewMenu()

##### Basic Controls
    
    def up(self):
        self["downloadmenu"].up()
        self.loadInfo()
    
    def down(self):
        self["downloadmenu"].down()
        self.loadInfo()
    
    def left(self):
        self["downloadmenu"].pageUp()
        self.loadInfo()
    
    def right(self):
        self["downloadmenu"].pageDown()
        self.loadInfo()

##### % Anzeige

class BufferThread():
    def __init__(self):
        self.progress = 0
        self.downloading = False
        self.error = ""
        self.download = None
    
    def startDownloading(self, filename, url):
        self.progress = 0
        self.downloading = True
        self.error = ""
        self.download = downloadWithProgress(url, filename)
        self.download.addProgress(self.httpProgress)
        self.download.start().addCallback(self.httpFinished).addErrback(self.httpFailed)
    
    def httpProgress(self, recvbytes, totalbytes):
        self.progress = int(100 * recvbytes / float(totalbytes))
    
    def httpFinished(self, string=""):
        self.downloading = False
        if string is not None:
            self.error = str(string)
        else:
            self.error = ""

    
    def httpFailed(self, failure_instance=None, error_message=""):
        self.downloading = False
        if error_message == "" and failure_instance is not None:
            error_message = failure_instance.getErrorMessage()
            self.error = str(error_message)
    
    def stop(self):
        self.progress = 0
        self.downloading = False
        self.error = ""
        self.download.stop()

bufferThread = BufferThread()

##### Downloader

class downloadfile(Screen):
    skin = """
        <screen name="downloadfile" position="center,center" size="300,300" title="Download File" >
                <widget name="info" position="0,5" size="290,200" font="Regular;18" transparent="1" backgroundColor="#415a80" halign="center" valign="center" />
                <widget name="progress" position="10,200" size="280,14" backgroundColor="#415a80" pixmap="skin_default/progress_big.png" borderWidth="2" borderColor="#cccccc" />
                <widget name="precent" position="125,225" size="50,20" font="Regular;19" halign="center" valign="center" backgroundColor="#415a80" zPosition="6" />
                <ePixmap name="red" position="10,260" zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                <ePixmap name="green" position="150,260" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                <widget name="key_red" position="10,260" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green" position="150,260" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""
    
    def __init__(self, session, filename, url):
        self.session = session
        self.skin = downloadfile.skin
        Screen.__init__(self, session)
        self.url = url
        self.filename = filename
        self.infoTimer = eTimer()
        self.infoTimer.timeout.get().append(self.updateInfo)
        self.Shown = True
        self["info"] = Label(_("Downloading Plugin: %s") % self.filename)
        self["progress"] = ProgressBar()
        self["precent"] = Label()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
                                    {
                                     "ok": self.okClicked,
                                     "cancel": self.exit,
                                     "green": self.okClicked,
                                     "red": self.exit
                                     }, -1)
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Show/Hide"))
        self.onLayoutFinish.append(self.downloadPlugin)

    def downloadPlugin(self):
        bufferThread.startDownloading(self.filename, self.url)
        self.infoTimer.start(300, False)

    def updateInfo(self):
        if bufferThread.error != "":
            self["info"].setText(bufferThread.error)
            self.infoTimer.stop()
        else:
            progress = int(bufferThread.progress)
            self["progress"].setValue(progress)
            self["precent"].setText(_("%s%%") % (progress))
            if progress == 100:
                self.infoTimer.stop()
                self.session.openWithCallback(self.install, MessageBox, _("Download complete. Install now?"), MessageBox.TYPE_YESNO).setTitle(_("Install?"))
                self.close(True)

    def okClicked(self):
        if self.Shown == True:
            self.hide()
            self.Shown = False
        else:
            self.show()
            self.Shown = True
    
    def exit(self):
        self.session.openWithCallback(self.StopDownLoad, MessageBox, _("Do you realy want to stop the download?"), MessageBox.TYPE_YESNO).setTitle(_("Abort Download?"))
    
    def StopDownLoad(self, result):
        if result is True:
            bufferThread.download.stop()
            self.close(None)
        else:
            pass
    
    def install(self, answer):
        if answer is True:
            self.doInstall()
    
    def doInstall(self):
        if "tar.gz" in  self.filename:
            os.system("tar xzf " + self.filename + " -C /")
        elif "tgz" in  self.filename:
            os.system("tar xzf " + self.filename + " -C /")
        elif "ipk" in  self.filename:
            # Installiert das Plugin und liest den expliziten Pluginnamen (wichtig fuer remove)
            os.system("ipkg install " + self.filename + " | cut -d' ' -f2 | sort -u > /tmp/.ipkinst")
            # das ist der Pluginname
            pluginname = open("/tmp/.ipkinst", "r").readline()
            
            # Erklaerung:
            # Splittet vom Dateinamen Bsp: enigma2-plugin-extensions-cccaminfo_svn-2940-r0_all.ipk anhand von "-" und waehlt den 4 Teil aus
            # -> cccaminfo_svn-2940-r0_all.ipk
            # Jetzt wird noch am "_" gesplittet und der erste Teil ausgewaehlt -> cccaminfo
            if pluginname.split('-')[0] == "enigma2":
                f = open("/usr/uninstall/hdf_" + self.filename.split("-")[3].split('_')[0] + "_delfile_ipk.sh", 'w')
                print >> f, '#!/bin/sh \n\n', 'ipkg remove ' + pluginname, '\nrm -rf /usr/uninstall/hdf_' + self.filename.split("-")[3].split("_")[0] + '_delfile_ipk.sh'
                f.close()
                os.chmod("/usr/uninstall/hdf_" + self.filename.split("-")[3].split('_')[0] + "_delfile_ipk.sh", 755)
            else:
                pass
        os.remove(self.filename)

###########################################################################

class PictureScreen(Screen):
    
    skin="""
        <screen name="Preview" position="center,center" size="800,450" title="Preview" >
            <widget name="picture" position="0,0" size="800,450" zPosition="1" alphatest="on" />
        </screen>"""
    
    def __init__(self, session, picPath = None):
        Screen.__init__(self, session)
        self.picPath = picPath
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["picture"] = Pixmap()
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
            "ok": self.cancel,
            "cancel": self.cancel
        }, -1)
        
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)
    
    def ShowPicture(self):
        if self.picPath is not None:
            self.PicLoad.setPara([
                        self["picture"].instance.size().width(),
                        self["picture"].instance.size().height(),
                        self.Scale[0],
                        self.Scale[1],
                        0,
                        1,
                        "#002C2C39"])
            
            self.PicLoad.startDecode(self.picPath)
    
    def DecodePicture(self, PicInfo = ""):
        if self.picPath is not None:
            ptr = self.PicLoad.getData()
            self["picture"].instance.setPixmap(ptr)

    
    def cancel(self):
        self.close(None)

###### Standard Stuff

#def Plugins(**kwargs):
#    return [PluginDescriptor(
#                            name="HDF Downloader " + boxname,
#                            description=_("HDF Downloader"),
#                            icon="hdf.png",
#                            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
#                            fnc=main),
#                            PluginDescriptor(name="HDF Downloader " + boxname,
#                            description=_("HDF Downloader"),
#                            icon="hdf.png",
#                            where=PluginDescriptor.WHERE_PLUGINMENU,
#                            fnc=main)]

def main(session, **kwargs):
    session.open(Hdf_Downloader)

#Recent Updates:
# Die Discription tut
# descrition und size widgets  von center/center auf left/top gesetzt
# Download schreibt keine scheisse mehr
# Namen im Menu werden jetzt ohne Dateiendung angezeigt
# datenbank datei umbenannt von test.txt zu down.hdf
# TryQuitMainloop tut
# Crash Bei Kategorie Wechsel gefixt...
# einlesen ueberprueft jetzt switch switch + "s" und switch + "shd"
## so liest er zum Beispiel picon, picons und piconshd alle in eine liste
# Download + Install tut jetzt.. finally
# Uninstaller hinzugefuegt
# Labels und StaticTexte je nach Situation agepasst
# Messegabox Titles angepasst
# Message Boxes Angepasst
# Ordentlich Sortiert
# Skin Titel zu loadInfo hinzugefuegt ;)
# uninstall angepasst neuer dateiname bsp: hdf_Noad_delfile_gz.sh
## bzw hdf_cccaminfo_delfile_ipk_sh
# beim installieren von ipk dateien wird eine hdf_*_delfile_ipk.sh erstellt
# Preview fuer Skins eingebaut
# install Option fuer tar.gz, tgz, ipk von /tmp
# vuduo cpu info fix
# Rueckmeldung beim tmp install hinzugefuegt
# os.chmod beim uninstall hinzugefuegt
# os.remove der datei im tmp nach download angepasst
# Zuron-One hinzugefuegt mit folder vom et9000
# tmpinstall im def ok geaendert: bei xxx.aaa.ipk wurde aaa als filetype erkannt, jetzt ists eine schleife ueber die laenge des am . getrennten dateinamens 
# Unterscheidung vusolo und gigablue eingebaut
# Umgebaut auf allgemeinen feed ohne unterordner
# .devdown datei eingebaut um alle Boxtypen im downloadmenu zu haben, nicht nur den eigenen
# plugin selbst reload ohne enigma restart eingebaut
# Menubutton zum Manuellen recompile eingebaut # tut nur, wenn .devdown aktiv ist
# ipkg check und symlink eingebaut
# Liste 0 Sortiert
# selbst loeschen der py eingefuegt
# uninstall ordner wird angelegt falls nicht vorhanden
# check auf python 2.7 
## -> falls ja: mips23el einlesen
#added gbquad as boxtype
#added tmtwin as boxtype
