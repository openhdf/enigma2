#
# Menu Fantastic Plugin by gutemine
#
import os

#check the box
menulog = open("/proc/cpuinfo","r")
for line in menulog: 
   if "BCM7413B1 STB platform" in line:
      box = "ET9x00"
   elif "BCM7335B0 STB platform" in line:
      box = "Vu+Duo"
   elif "NXP STB22x" in line:
      box = "TM800"
   elif "STx7109" in line:
      box = "IPBox"
   elif "STx7111" in line:
      box = "Spark"
   elif os.path.exists("/proc/stb/info/boxtype"):
      if open("/proc/stb/info/boxtype",'r').read().strip() == "gigablue":
         box = "GigaBlue"
   elif "BCM7325B0 STB platform" and "220.16" in line:
      box = "Vu+Solo"
   elif "BCM97xxx Settop Platform" in line:
      if open("/proc/stb/info/boxtype",'r').read().strip() == "Ixuss One":
         box = "Ixuss"
         boxname = "Ixuss One"
      if open("/proc/stb/info/boxtype",'r').read().strip() == "Zuron One":
         box = "Zuron"
         boxname = "Zuron One"
   elif "BCM7346B2" in line:
      box = "GigaBlue"
if os.path.exists("/proc/stb/info/hwmodel"):
   if open("/proc/stb/info/hwmodel",'r').read().strip() == "twin":
      box = "TM-Twin"

menulog.close()

os.system("cat /proc/cpuinfo > /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.cpuinfo")
os.system("echo " + box + " > /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.boxtype")
os.system("chmod 755 -R /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox")

if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/menu") is False or os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/scripts") is False:	
   os.system("mv /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/boxtypes/" + box + "/* /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/")
   os.system("rm -rf /usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/boxtypes/")
   
from enigma import *
from Screens.Screen import Screen
from Screens.Standby import *
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.GUIComponent import *
from Components.MenuList import MenuList
from Components.Input import Input
from Screens.Console import Console
from Screens.About import *
from Plugins.Plugin import PluginDescriptor
from RecordTimer import *
from time import *
from Tools import Directories, Notifications
import NavigationInstance
import downloader
#try:
#   import downloader
#except:
#   pass
   
#def HDF_Downloader(self):
#   self.session.open(downloader.Hdf_Downloader)

# plugin calling support comes here ...
pluginpath = "/usr/lib/enigma2/python/Plugins/"

from Screens.Ci import *
from Screens.PluginBrowser import *

if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/.autoupdate") is True:
   os.system("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/update.sh")

if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/plugin.py"):
    os.remove("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/plugin.py")
else:
    pass

# SoftcamManager
if os.path.exists("%s/Extensions/SoftcamManager" %pluginpath) is True:
   from Plugins.Extensions.SoftcamManager.Sc import *
if os.path.exists("/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup") is True:
   from Plugins.PLi.SoftcamSetup.Sc import *
# SkinSelector
if os.path.exists("%s/SystemPlugins/SkinSelector" %pluginpath) is True:
   try:
      from Plugins.SystemPlugins.SkinSelector.plugin import *
   except:
      pass
# SoftwareUpdate
if os.path.exists("%s/SystemPlugins/SoftwareUpdate" %pluginpath) is True:
  try:
     from Plugins.SystemPlugins.SoftwareUpdate.plugin import *
  except:
     pass
 
   
fantastic_pluginversion = "Version 0.1.2 .. HDF mod"
fantastic_pluginpath = "/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox"
fantastic_readme = "/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/readme.txt"
splitchar = ":"


session = None


def autostart(reason, **kwargs):
    global session
    if reason == 0 and kwargs.has_key("session"):
       session = kwargs["session"]
       session.open(FantasticBoot)
       
def menu(menuid, **kwargs):
    if menuid == "mainmenu":
        return [(_("HDF Toolbox " + box + ""), main, "hdf_toolbox", 10)]
    return []
	
def Plugins(**kwargs):
    try:
	return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart),
			PluginDescriptor(name=" HDF Toolbox " + box + "", description="Addons, Scripts, Tools", where = PluginDescriptor.WHERE_EXTENSIONSMENU, icon="hdf.png", fnc=main),
            PluginDescriptor(name="HDF Toolbox " + box + "", description="Addons, Scripts, Tools", where = PluginDescriptor.WHERE_MENU, fnc=menu),
            PluginDescriptor(where = PluginDescriptor.WHERE_FILESCAN, fnc = filescan)]
    except:
	return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart),PluginDescriptor(name="HDFreaks Toolbox " + box + "", description="Addons, Scripts, Tools", where = [PluginDescriptor.WHERE_PLUGINMENU , PluginDescriptor.WHERE_EXTENSIONSMENU], icon="hdf.png", fnc=main),PluginDescriptor(name = "HDFreaks Toolbox " + box + "", description = "Addons, Scripts, Tools", where = PluginDescriptor.WHERE_MENU, fnc = menu)]
	 
def main(session,**kwargs):
    try:    
     	session.open(Fantastic)
    except:
        print "[FANTASTIC] Pluginexecution failed"

class Fantastic(Screen):
    skin = """
        <screen position="150,150" size="360,395" title="HDF Toolbox">
        <widget name="menu" position="10,10" size="340,340" scrollbarMode="showOnDemand" enableWrapAround="1" />
		<ePixmap position="10,335" size="380,57" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/banner.png" zPosition="1" alphatest="on" />
        <eLabel text="Version .OE. 16.08.2012" position="205,315" size="990,45" font="Regular;12" valign="right" transparent="1" />
        </screen>"""

    def __init__(self, session, args = 0):
        self.skin = Fantastic.skin
        self.session = session
        Screen.__init__(self, session)
        self.menu = args
        
        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument

        try:    
           if mfmenu is None:
              pass
        except:
           mfmenu="main"
           mfmenuold="main"
           mfmenudescr="Menu Fantastic Main Menu"

        if mfmenu is "red":
           pass
        elif mfmenu is "green":
           pass
        elif mfmenu is "yellow":
           pass
        elif mfmenu is "blue":
           pass
        else:
           mfmenu="main"
           mfmenuold="main"
           mfmenudescr="Menu Fantastic Main Menu"

        mfexecute=" "
        mfintargument=0
        mftextargument=" "
                
        mainmenu = []

        menufile = "%s/%s.cfg" % (fantastic_pluginpath,mfmenu)
        if os.path.exists(menufile) is True:
           mf = open(menufile,"r")
           for line in mf:
              parts=line.split(splitchar,3)
              index=len(parts)
   
              if index > 1:
                 command=parts[0].upper().rstrip()
                 mfcommand=command[0]
                 if mfcommand is not "S":
                    if index >2:
                       mainmenu.append(( str(parts[2]), line ))
                    else:
                       mainmenu.append(( str(parts[1]), line ))
 
           mf.close()
        else:
           mainmenu.append(("no %s.cfg found - please reboot" %mfmenu, "mfnomenu"))        

        if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HDF-Toolbox/hdf.png") is True:
           mainmenu.append(("HDF-Downloader" , "mfschdf"))
		   
		# SoftcamManager
        if os.path.exists("%s/Extensions/SoftcamManager" %pluginpath) is True:
           mainmenu.append(("Softcam Cardserver Manager", "mfsc"))
           mainmenu.append((" " , "mfxyz"))
           mainmenu.append(("About" , "mfabout"))
        elif os.path.exists("/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup") is True:
           mainmenu.append(("Softcam Cardserver Manager", "mfsc"))
           mainmenu.append((" " , "mfxyz"))
           mainmenu.append(("About" , "mfabout"))		   
        else:
           mainmenu.append(("About" , "mfabout"))     

        self["menu"] = MenuList(mainmenu)
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"],{"ok": self.FantasticMainMenu,"back": self.close,}, -1)
        
    def FantasticMainMenu(self):

        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument

        mfselected = self["menu"].l.getCurrentSelection()[1]

        if mfselected is not None:
           if mfselected is "mfreadme":
                self.session.open(Console,_("Showing Fantastic readme.txt"),["cat %s" % fantastic_readme])
           elif mfselected is "mfnomenu":
               title1=_("HDF-Toolbox") 
               title2=_("needs a %s.cfg file at" % mfmenu)
               title3=_("%s" %fantastic_pluginpath)
               title="%s\n%s\n%s" % (title1, title2,title3)
               self.session.open(MessageBox,("%s") % (title),  MessageBox.TYPE_INFO)
           elif mfselected is "mfabout":
               title1=_("Menu Fantastic Plugin %s") % fantastic_pluginversion
               title2=_("by gutemine is Freeware - use at your own risk !")
               title3=_("~~~~~~~~~~~~~~~~~~~~~~~~~")
               title4=_("adapted by www.hdfreaks.cc")
               title="%s\n%s\n%s\n%s" % (title1, title2, title3, title4)
               self.session.open(MessageBox,("%s") % (title),  MessageBox.TYPE_INFO)
           elif mfselected is "mfschdf":
               #self.session.openWithCallback(self.FantasticMenu(""),HDF_Downloader)
               self.session.open(downloader.Hdf_Downloader)
               #self.HDF_Downloader()
           elif mfselected is "mfsc":
               self.session.openWithCallback(self.FantasticMenu(""),ScSelection)
           elif mfselected is "mfsc2":
               self.session.openWithCallback(self.FantasticMenu(""),ScSelection2)
           elif mfselected is "mfxyz":
               title1=_("HDF Toolbox")
               title2=_("~~~~~~~~~~~~~~~~")
               title3=_("visit www.HDFreaks.cc for updates and support")
               title="%s\n%s\n%s\n" % (title1, title2, title3)
               self.session.open(MessageBox,("%s") % (title),  MessageBox.TYPE_INFO)
           else:
               self.FantasticMenuSelected(mfselected)

    def FantasticMenu(self,status):

        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument

        if mfmenu is None:
           self.skipMF("No menu passed, returning")
        else:
           mfmenufile = "%s/%s.cfg" % (fantastic_pluginpath,mfmenu.rstrip())
           if os.path.exists(mfmenufile) is True:
              mf = open(mfmenufile,"r")
              line=mf.readline()
              mf.close()
              parts=line.split(splitchar,3)
              index=len(parts)
              if index > 1:
                 command=parts[0].upper().rstrip()
                 # only if menu file contains S in first line startup is executed
                 if command[0] is "S":
                    if index > 3:
                       cmd=parts[3].rstrip()
                       if mfmenu == mfmenuold:
                          pass
                       elif mfmenu == "main":
                          pass
                       else:
                          if os.path.exists("%s/%s" %(fantastic_pluginpath,cmd)) is True:
                             os.system("%s/%s %s" % (fantastic_pluginpath,cmd,mftextargument))
                          else:
                             os.system("%s %s" % (cmd,mftextargument))
                       
                       mfmenudescr=parts[2].rstrip()
                    else:
                       if index is 3:
                          mfmenudescr=parts[2].rstrip()
                       else:
                          mfmenudescr=parts[1].rstrip()
                          
           if os.path.exists("%s/%s.cfg" % (fantastic_pluginpath,mfmenu.rstrip())) is True:
              if mfmenu == "main":
                 pass
              else:
                 self.session.openWithCallback(self.FantasticMenuSelected,ChoiceBox,mfmenudescr,self.ListMenuFantastic())        
           else:
              self.skipMF("no Menufile %s.cfg" %mfmenu)

    def FantasticMenuSelected(self,mfselected):

        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument


        if mfselected is None:
#           self.skipMF("nothing selected")
           mfmenu="main"
        else:
           try:
              parts=mfselected.split(splitchar,4)
           except:
              parts=mfselected[1].split(splitchar,4)

           mfcommand=" "
           mfexecute=" "
           mfintargument=0
           mftextargument=" "

           index=len(parts)
           if index > 1:
              command=parts[0].upper().rstrip()
              mfcommand=command[0]
           else:
              command=" "
              mfcommand=command[0]

           if index > 1:
              mfmenuold=mfmenu
              mfmenu=parts[1].rstrip()

           if index > 2:
              mfmenudescr=parts[2].rstrip()
           else:
              mfmenudescr=parts[1].rstrip()
              
           if index > 3:
              mfexecute=parts[3].rstrip()
              mftextargument=parts[3].rstrip()

           if index > 4:
              mftextargument=parts[4].rstrip()
              try:
                 mfintargument=int(mftextargument)
              except:
                 mfintargument = 0
           elif index == 4:
              mftextargument=parts[3].rstrip()
              try:
                 mfintargument=int(mftextargument)
              except:
                 mfintargument = 0
           else:
              pass

           if mfcommand is "E":
              if os.path.exists("%s/%s" % (fantastic_pluginpath,mfexecute)) is True:
                 os.system("%s/%s %s" % (fantastic_pluginpath,mfexecute,mftextargument))
              else:
                 os.system("%s %s"  % (mfexecute,mftextargument))
              self.session.openWithCallback(self.FantasticMenu,MessageBox,"%s %s was executed !" %(mfexecute,mftextargument), MessageBox.TYPE_INFO, timeout=mfintargument)
# patched by barabas
           elif mfcommand is "U":
              if os.path.exists("%s/%s" % (fantastic_pluginpath,mfexecute)) is True:
                 os.system("%s/%s %s" % (fantastic_pluginpath,mfexecute,mftextargument))
              else:
                 os.system("%s %s"  % (mfexecute,mftextargument))
              self.FantasticMenu("") 
# ------ ende ------              
           elif mfcommand is "C":
              if os.path.exists("%s/%s" % (fantastic_pluginpath,mfexecute)) is True:
                 self.session.openWithCallback(self.FantasticMenu(""),Console,_("Executing %s %s" %(mfexecute, mftextargument)),["%s/%s %s" % (fantastic_pluginpath,mfexecute,mftextargument) ])
              else:
                 self.session.openWithCallback(self.FantasticMenu(""),Console,_("Executing %s %s" %(mfexecute, mftextargument)),["%s %s" % (mfexecute, mftextargument) ])
           elif mfcommand is "A":
              FantasticApplication(self.session)
              self.FantasticMenu("")
           elif mfcommand is "P":
              plugininstalled=False
              if os.path.exists("%s/Extensions/%s" %(pluginpath,mftextargument)) is True:
                 plugininstalled=True
              if os.path.exists("%s/SystemPlugins/%s" %(pluginpath,mftextargument)) is True:
                 plugininstalled=True
                 
              if plugininstalled is True:
                 if mftextargument == "Tuxtxt":
                    self.session.openWithCallback(self.FantasticMenu(""),ScSelection)
                 elif mftextargument == "SoftcamManager":
                    self.session.openWithCallback(self.FantasticMenu(""),ScSelection)
                 elif mftextargument == "BarryAllen":
                    self.session.openWithCallback(self.FantasticMenu(""),BarryAllenPlugin)
                 elif mftextargument == "Multiboot":
                    self.session.openWithCallback(self.FantasticMenu(""),Multiboot)
                 elif mftextargument == "MediaPlayerDeluxe":
                    self.session.openWithCallback(self.FantasticMenu(""),MediaPlayerDeluxe)                                     
                 elif mftextargument == "SpiderFan":
                    self.session.openWithCallback(self.FantasticMenu(""),SpiderFan)
                 elif mftextargument == "Elektro":
                    self.session.openWithCallback(self.FantasticMenu(""),Elektro)
                 elif mftextargument == "Diabolius":
                    self.session.openWithCallback(self.FantasticMenu(""),Diabolius)
                 elif mftextargument == "Sakrileg":
                    self.session.openWithCallback(self.FantasticMenu(""),Sakrileg)
                 elif mftextargument == "Shell":
                    self.session.openWithCallback(self.FantasticMenu(""),Shell)
                 elif mftextargument == "Telefonbuch":
                    self.session.openWithCallback(self.FantasticMenu(""),Telefonbuch)
                 elif mftextargument == "PicturePlayer":
                    self.session.openWithCallback(self.FantasticMenu(""),picmain)
                 elif mftextargument == "ConfigurationBackup":
                    try:
                       self.session.openWithCallback(self.FantasticMenu(""),BackupSetup)
                    except:
                       pass  
		 elif mftextargument == "GboxSuite":
                    try:
                       self.session.openWithCallback(self.FantasticMenu(""),GboxSuite)
                    except:
                       pass  
		 elif mftextargument == "KeyUpdater":
                    try:
                       self.session.openWithCallback(self.FantasticMenu(""),KeyUpdater)
                    except:
                       pass  
		 elif mftextargument == "CCcamInfo":
                    try:
                       self.session.openWithCallback(self.FantasticMenu(""),CCcamInfo)
                    except:
                       pass  
		 elif mftextargument == "LasMail":
                    self.session.openWithCallback(self.FantasticMenu(""),LasMail)	
                 elif mftextargument == "Tuxcom":
                    self.session.openWithCallback(self.FantasticMenu(""),TuxComStarter)
                 elif mftextargument == "Cronmanager":
                    self.session.openWithCallback(self.FantasticMenu(""),Cronmanager)
                 elif mftextargument == "TuxboxGames":
                    self.session.openWithCallback(self.FantasticMenu(""),GameStarter)
                 elif mftextargument == "FrontprocessorUpgrade":
                    self.session.openWithCallback(self.FantasticMenu(""),FPUpgrade)
                 elif mftextargument == "SoftwareUpdate":
                    try:
                       self.session.openWithCallback(self.FantasticMenu(""),UpdatePluginMenu)
                    except:
		       pass
                 elif mftextargument == "weinbergtagger":
                    self.session.openWithCallback(self.FantasticMenu(""),weinbergtagger)
                 elif mftextargument == "SkinSelector":
                    try:
                       self.session.openWithCallback(self.FantasticMenu(""),SkinSelector)
                    except:
                       self.session.openWithCallback(self.FantasticMenu,MessageBox,"Plugin %s is not wrapped !" %mftextargument, MessageBox.TYPE_INFO)
                 else:
                    self.session.openWithCallback(self.FantasticMenu,MessageBox,"Plugin %s is not wrapped !" %mftextargument, MessageBox.TYPE_INFO)
              else:
                 if mftextargument == "Ci":
                    self.session.openWithCallback(self.FantasticMenu(""),CiSelection)
                 elif mftextargument == "BP":
                    if os.path.exists("/usr/lib/enigma2/python/Bp") is True:
                       try:
                          self.session.openWithCallback(self.FantasticMenu(""),BPmenu)
                       except:
                          self.session.openWithCallback(self.FantasticMenu(""),BP_Menu)
                    else:
                       self.session.openWithCallback(self.FantasticMenu,MessageBox,"Plugin %s is not available !" %mftextargument, MessageBox.TYPE_INFO)
                 else:
                    self.session.openWithCallback(self.FantasticMenu,MessageBox,"Plugin %s is not installed !" %mftextargument, MessageBox.TYPE_INFO)
                    
           elif mfcommand is "R":
              if mfintargument == 3:
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,"Restarting Enigma2", MessageBox.TYPE_INFO, timeout=5)
                 TryQuitMainloop(self.session,mfintargument)
              elif mfintargument == 2:
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,"Restarting Dreambox", MessageBox.TYPE_INFO, timeout=5)
                 TryQuitMainloop(self.session,mfintargument)
              elif mfintargument == 1:
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,"Entering Deepstandby", MessageBox.TYPE_INFO, timeout=5)
                 TryQuitMainloop(self.session,mfintargument)
              else:
                 pass
           elif mfcommand is "I":
              if os.path.exists("%s/%s.txt" %(fantastic_pluginpath,mfexecute)) is True:
                 menufile="%s/%s.txt" %(fantastic_pluginpath,mfexecute)
                 mf = open(menufile,"r")
                 mfexecute=mf.readline()
                 mf.close()
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,mfexecute, MessageBox.TYPE_INFO, timeout=mfintargument)
              elif os.path.exists("/tmp/%s.txt" %(mfexecute)) is True:
                 menufile="/tmp/%s.txt" %(mfexecute)
                 mf = open(menufile,"r")
                 mfexecute=mf.readline()
                 mf.close()
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,mfexecute, MessageBox.TYPE_INFO, timeout=mfintargument)
              else:
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,mfexecute, MessageBox.TYPE_INFO, timeout=mfintargument)

# modded by koivo G: read file
           elif mfcommand is "G":
              if os.path.exists("%s" % (mfexecute)) is True:
                 os.system("%s %s" % (mfexecute,mftextargument))
                 datei = open(mftextargument,"r")
                 Ausgabe=datei.read()
                 datei.close()
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,Ausgabe, MessageBox.TYPE_INFO)
# modded by koivo Q: execute and read file
           elif mfcommand is "Q":
                 os.system("%s>%s"  % (mfexecute,mftextargument))
                 datei = open(mftextargument,"r")
                 Ausgabe=datei.read(400)
                 datei.close()
                 self.session.openWithCallback(self.FantasticMenu,MessageBox,Ausgabe, MessageBox.TYPE_INFO, timeout=mfintargument)
# modded by koivo Q: execute and read file with yes or no
           elif mfcommand is "X":
                 os.system("%s>%s"  % (mfexecute,mftextargument))
                 datei = open(mftextargument,"r")
                 Ausgabe=datei.read()
                 datei.close()
                 self.session.openWithCallback(self.FantasticYN,MessageBox,Ausgabe, MessageBox.TYPE_YESNO)			  
# modded by koivo Z: open extra plugins and screens
           elif mfcommand is "Z":
                 self.session.openWithCallback(self.FantasticMenu(""),PluginBrowser)
           elif mfcommand is "1":
                 self.session.openWithCallback(self.FantasticMenu(""),UpdatePluginMenu)
				 
				 
           elif mfcommand is "D":
#              self.session.open(FantasticLCD,mftextargument)
              self.session.openWithCallback(self.FantasticMenu(""),FantasticLCD,mftextargument)

           elif mfcommand is "L":
              if mftextargument == "log":
                 os.system("echo %s > /tmp/fantasticlog.txt" %mfexecute) 
              elif mftextargument == "logappend":
                 os.system("echo %s >> /tmp/fantasticlog.txt" %mfexecute) 
              elif mftextargument == "reset":
                 if os.path.exists("/tmp/fantasticlog.txt") is True:
                    os.system("rm /tmp/fantasticlog.txt") 
              elif mftextargument == "wall":
                 os.system("wall %s" %mfexecute) 
              else:
                 print "[FANTASTIC] Logging: %s" %mfexecute
              self.FantasticMenu("")
           elif mfcommand is "M":
              self.FantasticMenu("")
           elif mfcommand is "T":
              self.session.openWithCallback(self.FantasticEnterText,InputBox, title=mfmenudescr, text=mftextargument, maxSize=False, type=Input.TEXT)
           elif mfcommand is "Y":
              self.session.openWithCallback(self.FantasticYN,MessageBox,mfmenudescr, MessageBox.TYPE_YESNO)
           else:
              pass

    def ListMenuFantastic(self):

        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument

        menu = []

        menufile = "%s/%s.cfg" % (fantastic_pluginpath,mfmenu)
        mf = open(menufile,"r")

        for line in mf:
           parts=line.split(splitchar,3)
           index=len(parts)
           if index > 1:
              command=parts[0].upper().rstrip()
              if command[0] is not "S":
                 if index > 2:
                    menu.append(( str(parts[2]), line ))
                 else:
                    menu.append(( str(parts[1]), line ))
        mf.close()

        return menu

    def FantasticEnterText(self, mftext):

        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument

        if mftext is None:
           mftextargument = None
           mfmenu="main"
           self.skipMF("No text passed, Exiting menu %s" % mfmenu)
        else:
           mftextargument = mftext
           self.FantasticMenu("")


    def FantasticYN(self,mfanswer):

        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument

        if mfanswer is False:
           if mftextargument is not None:
              if mftextargument is not " ":
                 mfmenu=mftextargument
           
        self.FantasticMenu("")
           
    def skipMF(self,reason):
        self.session.open(MessageBox,_("Menu Fantastic exits, because %s") % reason, MessageBox.TYPE_WARNING)

class FantasticButton(Screen):
    def __init__(self,session,button):
	Screen.__init__(self,session)
	self.session = session

        global mfcommand
        global mfmenu
        global mfmenuold
        global mfexecute
        global mfmenudescr
        global mfintargument
        global mftextargument

        if button is not None:
           mfmenuold=button
           mfmenu=button
           mfmenudescr="Menu Fantastic %s Button Menu" %button
        else:
           mfmenuold="main"
           mfmenu="main"
           mfmenudescr="Menu Fantastic Main Menu"


class FantasticBoot(Screen):
        skin = """
            <screen position="100,100" size="500,400" title="HDFreaks.cc" >
            </screen>"""
        
	def __init__(self,session):
                self.skin = FantasticBoot.skin
		Screen.__init__(self,session)
		self.session = session
		
                mainmenufile = "%s/%s.cfg" % (fantastic_pluginpath,"main")
                if os.path.exists(mainmenufile) is True:
                   mfmain = open(mainmenufile,"r")
                   line=mfmain.readline()
                   parts=line.split(splitchar,3)
                   index=len(parts)
                   if index > 1:
                      command=parts[0].upper().rstrip()
                      # only if menu file contains S in first line startup is executed
                      if command[0] is "S":
                         if index > 3:
                            cmd=parts[3].rstrip()
                            if os.path.exists("%s/%s" %(fantastic_pluginpath,cmd)) is True:
                               os.system("%s/%s" % (fantastic_pluginpath,cmd))
                            else:
                               os.system("%s" % (cmd))
                            
                         mfmain.close()
   

class FantasticApplication(Screen):

        def __init__(self, session):
                self.session = session
        	self.skin = Fantastic.skin
		Screen.__init__(self, session)
		self.container=eConsoleAppContainer()
		self.container.appClosed.get().append(self.finished)
		self.runapp()
		
	def runapp(self):
	
                global mfcommand
                global mfmenu
                global mfmenuold
                global mfexecute
                global mfmenudescr
                global mfintargument
                global mftextargument

		eDBoxLCD.getInstance().lock()
		eRCInput.getInstance().lock()
		fbClass.getInstance().lock()
                self.session.nav.stopService()
                if os.path.exists(mfexecute) is True:
 		   self.container.execute("%s %s" %(mfexecute,mftextargument))
 		else:
 		   self.container.execute("%s/%s %s" %(fantastic_pluginpath,mfexecute,mftextargument))

	def finished(self,retval):
		fbClass.getInstance().unlock()
		eRCInput.getInstance().unlock()
		eDBoxLCD.getInstance().unlock()
		self.session.nav.playService(eServiceReference(config.tv.lastservice.value))



class FantasticLCD(Screen):
        # use size 0,0 to show text on LCD only
	skin = """
		<screen position="0,0" size="0,0" title="LCD Text" >
			<widget name="text" position="0,0" size="0,0" font="Regular;14" halign="center"/>
		</screen>"""
		
	def __init__(self, session, title = "LCD Text"):
		self.skin = FantasticLCD.skin
		Screen.__init__(self, session)

		self["text"] = Label("")

                # minimal actions to be able to exit after showing LCD Label
		self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
		{
			"ok": self.cancel,
			"back": self.cancel,
		}, -1)
                # now set passed Text Label for LCD output 		
		self.newtitle = title
		self.onShown.append(self.updateTitle)

	def updateTitle(self):
		self.setTitle(self.newtitle)
			
	def cancel(self):
		self.close()



