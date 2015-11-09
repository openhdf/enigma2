from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from ExtrasList import ExtrasList

def MessageBoxEntry(name, picture):
    res = [(name, picture)]
    picture = '/usr/lib/enigma2/python/Plugins/SystemPlugins/DeviceManager/icons/' + picture
    if fileExists(picture):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 0), size=(48, 48), png=loadPNG(picture)))
    res.append(MultiContentEntryText(pos=(65, 10), size=(425, 38), font=0, text=name))
    return res


class ExtraMessageBox(Screen):
    skin = '\n\t<screen name="ExtraMessageBox" position="80,100" size="560,400" title=" ">\n\t\t<widget name="message" position="10,10" size="540,25" font="Regular;20"/>\n\t\t<widget name="menu" position="10,90" size="540,360" scrollbarMode="showOnDemand" />\n\t\t<applet type="onLayoutFinish">\n# this should be factored out into some helper code, but currently demonstrates applets.\nfrom enigma import eSize, ePoint\n\norgwidth = self.instance.size().width()\norgpos = self.instance.position()\ntextsize = self[&quot;message&quot;].getSize()\n\n# y size still must be fixed in font stuff...\nif self[&quot;message&quot;].getText() != "":\n\ttextsize = (textsize[0] + 80, textsize[1] + 60)\nelse:\n\ttextsize = (textsize[0] + 80, textsize[1] + 4)\n\ncount = len(self.list)\nif count &gt; 7:\n\tcount = 7\noffset = 48 * count\nwsizex = textsize[0] + 80\nwsizey = textsize[1] + offset + 20\n\nif (640 &gt; wsizex):\n\twsizex = 640\nwsize = (wsizex, wsizey)\n\n# resize\nself.instance.resize(eSize(*wsize))\n\n# resize label\nself[&quot;message&quot;].instance.resize(eSize(*textsize))\n\n# move list\nlistsize = (wsizex - 20, 48 * count)\nself[&quot;menu&quot;].instance.move(ePoint(10, textsize[1] + 10))\nself[&quot;menu&quot;].instance.resize(eSize(*listsize))\n\n# center window\nnewwidth = wsize[0]\nself.instance.move(ePoint((1280-wsizex)/2, (720-wsizey)/(count &gt; 7 and 2 or 3)))\n\t\t</applet>\n\t</screen>'

    def __init__(self, session, message = '', title = '', menulist = [], type = 0, exitid = -1, default = 0, timeout = 0):
        Screen.__init__(self, session)
        self.skin = ExtraMessageBox.skin
        self.session = session
        self.ctitle = title
        self.exitid = exitid
        self.default = default
        self.timeout = timeout
        self.elapsed = 0
        self.list = []
        for item in menulist:
            self.list.append(MessageBoxEntry(item[0], item[1]))

        self['menu'] = ExtrasList(self.list)
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['message'] = Label(message)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.ok,
         'cancel': self.cancel}, -2)
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
            self.setTitle('%s - %d' % (self.ctitle, self.timeout - self.elapsed))
            self.timer.start(1000, 1)

    def layoutFinished(self):
        if self.timeout > 0:
            self.setTitle('%s - %d' % (self.ctitle, self.timeout))
        else:
            self.setTitle(self.ctitle)
        self['menu'].moveToIndex(self.default)

    def ok(self):
        index = self['menu'].getSelectedIndex()
        self.close(index)

    def cancel(self):
        if self.exitid > -1:
            self.close(self.exitid)